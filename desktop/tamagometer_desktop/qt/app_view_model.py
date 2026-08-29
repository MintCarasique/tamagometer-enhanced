"""Qt GUI-thread adapter around the existing serial and transfer services."""
from __future__ import annotations

from dataclasses import replace
import queue
import threading
from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot
from flipper_serial import FlipperConnection, IncompatibleCompanionError, find_flipper_port, list_ports
from transfer_status import TransferState
from .. import __version__
from ..catalog import categories_for, item_key, parse_item_key
from ..modes import MODES, get_mode
from ..settings import SettingsStore
from ..transfer import AppEvent, TransferController
from .catalog_model import CatalogModel

STATE_PROGRESS = {TransferState.PREPARING: .05, TransferState.WAITING_FIRST_MESSAGE: .2,
    TransferState.SENDING_ACKNOWLEDGEMENT: .4, TransferState.WAITING_GIFT_REQUEST: .55,
    TransferState.SENDING_GIFT: .8, TransferState.SENDING_RESULT: .8,
    TransferState.VERIFYING: .92, TransferState.COMPLETED: 1.0}

class AppViewModel(QObject):
    modeChanged=Signal(); themeChanged=Signal(); connectionChanged=Signal()
    transferChanged=Signal(); noticeChanged=Signal(); portsChanged=Signal()

    def __init__(self, settings_store=None, connection=None, port_provider=list_ports,
                 start_timer=True, parent=None):
        super().__init__(parent)
        self._store=settings_store or SettingsStore(); self._settings=self._store.load()
        self._mode=get_mode(self._settings.mode)
        self._catalog=CatalogModel(self._mode,self._settings.favorites,self._settings.recent,self)
        self._catalog.favoritesChanged.connect(self._save_favorites)
        self._catalog.selectionChanged.connect(self.transferChanged)
        self._connection=connection or FlipperConnection()
        self._port_provider=port_provider; self._ports=[]; self._selected_port=""
        self._connection_state="disconnected"; self._connection_status="Flipper disconnected"
        self._events=queue.Queue(); self._connection_results=queue.Queue()
        self._transfer=TransferController(self._connection,self._events)
        self._transfer_state="idle"; self._transfer_status="Ready"; self._progress=0.0; self._busy=False
        self._pending_key=""; self._notice_summary=""; self._notice_detail=""; self._notice_severity="info"
        self._poll_ticks=0
        self._timer=QTimer(self); self._timer.setInterval(80); self._timer.timeout.connect(self.drainEvents)
        if start_timer: self._timer.start()
        self.refreshPorts()
        candidate=find_flipper_port(self._ports,self._settings.port)
        if candidate:
            self._selected_port=candidate.device; self.portsChanged.emit()
            if self._settings.auto_connect: self._begin_connect(candidate.device)

    def _save(self,**changes): self._settings=replace(self._settings,**changes); self._store.save(self._settings)
    @Slot(object)
    def _save_favorites(self,values): self._save(favorites=tuple(values))
    def _notice(self,severity,summary,detail=""):
        self._notice_severity=severity; self._notice_summary=summary; self._notice_detail=detail; self.noticeChanged.emit()

    @Property(str,constant=True)
    def version(self): return __version__
    @Property(QObject,constant=True)
    def catalogModel(self): return self._catalog
    @Property("QVariantList",constant=True)
    def modes(self): return [{"key":m.key,"label":m.selector_label} for m in MODES.values()]
    @Property(str,notify=modeChanged)
    def modeKey(self): return self._mode.key
    @Property(str,notify=modeChanged)
    def pickerTitle(self): return self._mode.picker_title
    @Property(str,notify=modeChanged)
    def pickerHint(self): return self._mode.picker_hint
    @Property(str,notify=modeChanged)
    def instructions(self): return self._mode.instructions
    @Property(str,notify=modeChanged)
    def primaryActionLabel(self): return self._mode.send_label
    @Property(bool,notify=modeChanged)
    def legacyMode(self): return self._mode.key=="legacy"
    @Property("QStringList",notify=modeChanged)
    def categories(self): return list(categories_for(self._mode))
    @Slot(str)
    def setMode(self,key):
        mode=get_mode(key)
        if mode.key==self._mode.key or self._busy: return
        self._mode=mode; self._catalog.set_mode(mode); self._save(mode=mode.key)
        self.modeChanged.emit(); self.transferChanged.emit()
    @Property(bool,notify=themeChanged)
    def darkTheme(self): return self._settings.theme=="dark"
    @Slot()
    def toggleTheme(self): self._save(theme="light" if self.darkTheme else "dark"); self.themeChanged.emit()

    @Property("QVariantList",notify=portsChanged)
    def ports(self): return [{"device":p.device,"label":p.display_name} for p in self._ports]
    @Property(str,notify=portsChanged)
    def selectedPort(self): return self._selected_port
    @Property(int,notify=portsChanged)
    def selectedPortIndex(self): return next((i for i,p in enumerate(self._ports) if p.device==self._selected_port),-1)
    @Slot(str)
    def setSelectedPort(self,value): self._selected_port=value; self.portsChanged.emit()
    @Slot()
    def refreshPorts(self):
        self._ports=list(self._port_provider()); devices={p.device for p in self._ports}
        if self._selected_port not in devices:
            candidate=find_flipper_port(self._ports,self._settings.port); self._selected_port=candidate.device if candidate else ""
        self.portsChanged.emit()
    @Property(str,notify=connectionChanged)
    def connectionState(self): return self._connection_state
    @Property(str,notify=connectionChanged)
    def connectionStatus(self): return self._connection_status
    @Property(bool,notify=connectionChanged)
    def connected(self): return self._connection_state=="connected"
    def _begin_connect(self,port):
        if not port or self._connection_state in {"connecting","connected"}: return
        self._connection_state="connecting"; self._connection_status=f"Checking Companion · {port}"
        self.connectionChanged.emit(); self.transferChanged.emit()
        def worker():
            try: self._connection_results.put((True,port,self._connection.open(port)))
            except Exception as error: self._connection_results.put((False,port,error))
        threading.Thread(target=worker,daemon=True).start()
    @Slot()
    def toggleConnection(self):
        if self.connected:
            self._connection.close(); self._connection_state="disconnected"; self._connection_status="Flipper disconnected"
            self.connectionChanged.emit(); self.transferChanged.emit(); return
        if not self._selected_port:
            self._notice("error","No verified Flipper port selected.","Connect Flipper, open the Enhanced app, then refresh ports."); return
        self._begin_connect(self._selected_port)

    @Property(str,notify=transferChanged)
    def transferState(self): return self._transfer_state
    @Property(str,notify=transferChanged)
    def transferStatus(self): return self._transfer_status
    @Property(float,notify=transferChanged)
    def transferProgress(self): return self._progress
    @Property(bool,notify=transferChanged)
    def canStartTransfer(self): return self.connected and not self._busy and (self.legacyMode or self._catalog.selectedItemId>=0)
    @Property(bool,notify=transferChanged)
    def canCancelTransfer(self): return self._busy
    @Property(bool,notify=transferChanged)
    def canRepeatTransfer(self): return self.connected and not self._busy and parse_item_key(self._settings.last_transfer) is not None
    @Property(str,notify=transferChanged)
    def primaryActionHint(self):
        if not self.connected: return "Connect a verified Flipper before starting."
        if self._busy: return "Transfer active — keep both devices aligned."
        return "Ready. Follow the placement instructions, then start."
    @Slot()
    def startTransfer(self):
        if not self.canStartTransfer: return
        item_id=0 if self.legacyMode else self._catalog.selectedItemId
        name="Automatic game or gift" if self.legacyMode else self._catalog.selectedName
        self._pending_key=item_key(self._mode.key,item_id); self._progress=0; self._busy=True
        self._transfer.start(self._mode,item_id,name); self.transferChanged.emit()
    @Slot()
    def cancelTransfer(self): self._transfer.cancel()
    @Slot()
    def repeatLastTransfer(self):
        parsed=parse_item_key(self._settings.last_transfer)
        if not parsed or not self.connected or self._busy: return
        mode,item_id=parsed; self.setMode(mode.key)
        if mode.key!="legacy": self._catalog.select_key(item_key(mode.key,item_id))
        self.startTransfer()

    @Property(str,notify=noticeChanged)
    def noticeSummary(self): return self._notice_summary
    @Property(str,notify=noticeChanged)
    def noticeDetail(self): return self._notice_detail
    @Property(str,notify=noticeChanged)
    def noticeSeverity(self): return self._notice_severity
    @Slot()
    def dismissNotice(self): self._notice("info","")
    def _record_success(self):
        if not self._pending_key: return
        recent=[k for k in self._settings.recent if k!=self._pending_key]; recent.insert(0,self._pending_key)
        self._save(recent=tuple(recent[:12]),last_transfer=self._pending_key); self._catalog.set_recent(self._settings.recent); self._pending_key=""
    @Slot()
    def drainEvents(self):
        self._poll_ticks+=1
        if self._poll_ticks>=20:
            self._poll_ticks=0
            ports=list(self._port_provider()); devices={p.device.casefold() for p in ports}
            if self.connected and getattr(self._connection,"port","").casefold() not in devices:
                lost=getattr(self._connection,"port","") or "the selected port"
                self._connection.close(); self._connection_state="disconnected"; self._connection_status="Flipper disconnected"
                self._notice("error","Flipper was disconnected.",f"USB port {lost} is no longer available.")
                self.connectionChanged.emit(); self.transferChanged.emit()
            if [p.device for p in ports] != [p.device for p in self._ports]:
                self._ports=ports; self.portsChanged.emit()
        try:
            while True:
                ok,port,payload=self._connection_results.get_nowait()
                if ok:
                    self._connection_state="connected"; self._connection_status=f"Connected · {port} · Companion {payload.version}"
                    self._save(port=port); self._notice("success","Flipper connected and ready.")
                else:
                    self._connection_state="error"; self._connection_status="Flipper connection failed"
                    summary="The open Flipper app is incompatible." if isinstance(payload,IncompatibleCompanionError) else "Could not connect to Flipper."
                    self._notice("error",summary,str(payload))
                self.connectionChanged.emit(); self.transferChanged.emit()
        except queue.Empty: pass
        try:
            while True:
                event:AppEvent=self._events.get_nowait(); self._transfer_status=event.text
                if event.state:
                    self._transfer_state=event.state.value
                    self._progress=event.current/event.total if event.current is not None and event.total else STATE_PROGRESS.get(event.state,self._progress)
                if event.kind=="done": self._record_success(); self._notice("success",event.text)
                elif event.kind=="cancelled": self._pending_key=""; self._notice("info","Transfer cancelled.")
                elif event.kind in {"error","disconnected"}:
                    self._pending_key=""; self._notice("error","The transfer could not be completed.",event.text)
                    if event.kind=="disconnected": self._connection_state="disconnected"; self._connection_status="Flipper disconnected"; self.connectionChanged.emit()
                if event.kind in {"done","cancelled","error","disconnected"}: self._busy=False
                self.transferChanged.emit()
        except queue.Empty: pass
    @Slot()
    def shutdown(self): self._transfer.cancel(); self._connection.close()
