"""Mock camera for testing without real hardware."""

from datetime import datetime
from node.cameras.base import Camera
from node.capture.models import CaptureResult
import struct
import zlib


class MockCamera(Camera):
    """Generates fake PNG image data for testing."""
    
    def __init__(self, camera_id: str, node_id: str, width: int = 100, height: int = 100, exposure: float = 5.0, gain: float = 100.0):
        super().__init__(camera_id, node_id)
        self.width = width
        self.height = height
        self.exposure = exposure
        self.gain = gain
    
    def connect(self) -> None:
        """Mock connection."""
        self.connected = True
        print(f"Mock camera {self.camera_id} connected")
    
    def disconnect(self) -> None:
        """Mock disconnection."""
        self.connected = False
        print(f"Mock camera {self.camera_id} disconnected")
    
    def _create_simple_png(self) -> bytes:
        """Create a minimal valid PNG file."""
        # PNG signature
        png_sig = b'\x89PNG\r\n\x1a\n'
        
        # IHDR chunk (image header)
        width = self.width
        height = self.height
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        
        # IDAT chunk (image data) - grayscale ramp
        raw_data = b''
        for y in range(height):
            raw_data += b'\x00'  # filter type for each row
            for x in range(width):
                # Gradient: left to right, 0-255
                pixel = (x * 255) // width
                raw_data += bytes([pixel])
        
        compressed = zlib.compress(raw_data, 9)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        
        # IEND chunk
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        
        return png_sig + ihdr_chunk + idat_chunk + iend_chunk
    
    def capture_image(self) -> CaptureResult:
        """Generate a simple PNG image."""
        if not self.connected:
            raise RuntimeError("Camera not connected")
        
        image_bytes = self._create_simple_png()
        
        return CaptureResult(
            node_id=self.node_id,
            camera_id=self.camera_id,
            timestamp=datetime.utcnow(),
            image_bytes=image_bytes,
            exposure=self.exposure,
            gain=self.gain,
        )
    
    def get_info(self) -> dict:
        """Return camera info."""
        return {
            "camera_id": self.camera_id,
            "type": "MockCamera",
            "width": self.width,
            "height": self.height,
            "connected": self.connected,
        }

