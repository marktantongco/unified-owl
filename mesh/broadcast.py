"""
mesh/broadcast.py — P0-11 MeshHealthBroadcaster sidecar (extracted from forward_proxy.py:246 + mesh_alternatives.py)
UDP 239.255.255.250:42100 broadcast, peer pruning, TCP gossip fallback via OWL_MESH_MODE
"""
import asyncio, json, time, logging
from typing import Dict
logger = logging.getLogger("owl-mesh")

MESH_GROUP = "239.255.255.250"
MESH_PORT = 42100

class MeshHealthBroadcaster:
    def __init__(self, host="127.0.0.1", port=60000, max_connections=5, interval=30):
        self.host=host; self.port=port; self.max_connections=max_connections; self.interval=interval
        self.peers: Dict[str,float] = {}
        self._task=None

    async def start(self):
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Mesh broadcaster started {MESH_GROUP}:{MESH_PORT} every {self.interval}s")

    async def _loop(self):
        import socket
        while True:
            try:
                msg=json.dumps({"type":"owl-mesh","host":self.host,"port":self.port,"max_connections":self.max_connections,"ts":time.time()}).encode()
                sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                sock.sendto(msg, (MESH_GROUP, MESH_PORT))
                sock.close()
                # prune
                now=time.time()
                for k,v in list(self.peers.items()):
                    if now-v>90: del self.peers[k]
            except Exception as e:
                logger.debug(f"mesh broadcast failed: {e}")
            await asyncio.sleep(self.interval)

    def get_peer_count(self): return len(self.peers)
    def stop(self):
        if self._task: self._task.cancel()

