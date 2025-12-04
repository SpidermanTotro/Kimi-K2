#!/usr/bin/env python3
"""
THE FORGE AI - Multimodal Support Module
=========================================

Implements multimodal content support for "ChatGPT 2.0" including:
- Image handling and analysis
- Audio processing support
- Content type detection
- Cross-modal understanding
- Format conversion utilities

This module enables THE FORGE AI to work with various media types.
"""

import base64
import hashlib
import mimetypes
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware way"""
    return datetime.now(timezone.utc)


class ContentType(Enum):
    """Supported content types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    UNKNOWN = "unknown"


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"
    SVG = "svg"


class AudioFormat(Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"
    AAC = "aac"


@dataclass
class MultimodalContent:
    """Represents multimodal content"""
    content_id: str
    content_type: ContentType
    data: Union[str, bytes]  # Text or binary data
    mime_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    source: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = utc_now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "mime_type": self.mime_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "source": self.source,
            # Data is excluded for security - must be accessed directly
        }


@dataclass
class ImageAnalysis:
    """Result of image analysis"""
    format: str
    width: int
    height: int
    color_mode: str
    file_size: int
    has_transparency: bool
    dominant_colors: List[str] = field(default_factory=list)
    detected_objects: List[str] = field(default_factory=list)
    text_content: Optional[str] = None
    confidence: float = 0.0


@dataclass
class AudioAnalysis:
    """Result of audio analysis"""
    format: str
    duration_seconds: float
    sample_rate: int
    channels: int
    bitrate: int
    file_size: int
    has_speech: bool = False
    transcription: Optional[str] = None
    language: Optional[str] = None


class ContentDetector:
    """
    Detects and classifies content types
    """
    
    # MIME type mappings
    MIME_TO_CONTENT_TYPE = {
        # Text
        "text/plain": ContentType.TEXT,
        "text/html": ContentType.TEXT,
        "text/markdown": ContentType.TEXT,
        # Images
        "image/jpeg": ContentType.IMAGE,
        "image/png": ContentType.IMAGE,
        "image/gif": ContentType.IMAGE,
        "image/webp": ContentType.IMAGE,
        "image/bmp": ContentType.IMAGE,
        "image/svg+xml": ContentType.IMAGE,
        # Audio
        "audio/mpeg": ContentType.AUDIO,
        "audio/wav": ContentType.AUDIO,
        "audio/ogg": ContentType.AUDIO,
        "audio/flac": ContentType.AUDIO,
        "audio/mp4": ContentType.AUDIO,
        "audio/aac": ContentType.AUDIO,
        # Video
        "video/mp4": ContentType.VIDEO,
        "video/webm": ContentType.VIDEO,
        "video/ogg": ContentType.VIDEO,
        "video/quicktime": ContentType.VIDEO,
        # Documents
        "application/pdf": ContentType.DOCUMENT,
        "application/msword": ContentType.DOCUMENT,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ContentType.DOCUMENT,
        # Code
        "text/x-python": ContentType.CODE,
        "text/javascript": ContentType.CODE,
        "application/json": ContentType.CODE,
        "text/x-java-source": ContentType.CODE,
    }
    
    # File extension mappings
    EXTENSION_TO_CONTENT_TYPE = {
        # Text
        ".txt": ContentType.TEXT,
        ".md": ContentType.TEXT,
        ".html": ContentType.TEXT,
        # Images
        ".jpg": ContentType.IMAGE,
        ".jpeg": ContentType.IMAGE,
        ".png": ContentType.IMAGE,
        ".gif": ContentType.IMAGE,
        ".webp": ContentType.IMAGE,
        ".bmp": ContentType.IMAGE,
        ".svg": ContentType.IMAGE,
        # Audio
        ".mp3": ContentType.AUDIO,
        ".wav": ContentType.AUDIO,
        ".ogg": ContentType.AUDIO,
        ".flac": ContentType.AUDIO,
        ".m4a": ContentType.AUDIO,
        ".aac": ContentType.AUDIO,
        # Video
        ".mp4": ContentType.VIDEO,
        ".webm": ContentType.VIDEO,
        ".mov": ContentType.VIDEO,
        ".avi": ContentType.VIDEO,
        # Documents
        ".pdf": ContentType.DOCUMENT,
        ".doc": ContentType.DOCUMENT,
        ".docx": ContentType.DOCUMENT,
        # Code
        ".py": ContentType.CODE,
        ".js": ContentType.CODE,
        ".ts": ContentType.CODE,
        ".java": ContentType.CODE,
        ".cpp": ContentType.CODE,
        ".c": ContentType.CODE,
        ".go": ContentType.CODE,
        ".rs": ContentType.CODE,
        ".json": ContentType.CODE,
        ".yaml": ContentType.CODE,
        ".yml": ContentType.CODE,
    }
    
    @classmethod
    def detect_from_path(cls, file_path: str) -> ContentType:
        """Detect content type from file path"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        return cls.EXTENSION_TO_CONTENT_TYPE.get(ext, ContentType.UNKNOWN)
    
    @classmethod
    def detect_from_mime(cls, mime_type: str) -> ContentType:
        """Detect content type from MIME type"""
        return cls.MIME_TO_CONTENT_TYPE.get(mime_type.lower(), ContentType.UNKNOWN)
    
    @classmethod
    def detect_from_bytes(cls, data: bytes) -> ContentType:
        """Detect content type from file magic bytes"""
        # Check common magic bytes
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return ContentType.IMAGE
        elif data[:2] == b'\xff\xd8':
            return ContentType.IMAGE  # JPEG
        elif data[:6] in (b'GIF87a', b'GIF89a'):
            return ContentType.IMAGE
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return ContentType.IMAGE
        elif data[:3] == b'ID3' or data[:2] == b'\xff\xfb':
            return ContentType.AUDIO  # MP3
        elif data[:4] == b'RIFF' and data[8:12] == b'WAVE':
            return ContentType.AUDIO  # WAV
        elif data[:4] == b'OggS':
            return ContentType.AUDIO  # OGG
        elif data[:4] == b'fLaC':
            return ContentType.AUDIO  # FLAC
        elif data[4:8] == b'ftyp':
            return ContentType.VIDEO  # MP4/MOV
        elif data[:4] == b'%PDF':
            return ContentType.DOCUMENT
        else:
            # Try to decode as text
            try:
                data[:1024].decode('utf-8')
                return ContentType.TEXT
            except UnicodeDecodeError:
                return ContentType.UNKNOWN
    
    @classmethod
    def get_mime_type(cls, file_path: str) -> str:
        """Get MIME type for a file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"


class ImageHandler:
    """
    Handles image processing and analysis
    
    Note: For full image processing, PIL/Pillow would be required.
    This implementation provides basic functionality without external dependencies.
    """
    
    @staticmethod
    def load_image(file_path: str) -> Optional[MultimodalContent]:
        """Load an image from file"""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Image file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            content_id = hashlib.sha256(data).hexdigest()[:16]
            mime_type = ContentDetector.get_mime_type(file_path)
            
            return MultimodalContent(
                content_id=content_id,
                content_type=ContentType.IMAGE,
                data=data,
                mime_type=mime_type,
                metadata={
                    "filename": path.name,
                    "file_size": len(data)
                },
                source=file_path
            )
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def to_base64(image_data: bytes) -> str:
        """Convert image data to base64 string"""
        return base64.b64encode(image_data).decode('utf-8')
    
    @staticmethod
    def from_base64(base64_string: str) -> bytes:
        """Convert base64 string to image data"""
        return base64.b64decode(base64_string)
    
    @staticmethod
    def analyze_image(image_data: bytes) -> ImageAnalysis:
        """
        Analyze image properties
        
        Note: This is a basic implementation. Full analysis would require
        image processing libraries like PIL/Pillow.
        """
        # Detect format from magic bytes
        format_detected = "unknown"
        width = 0
        height = 0
        color_mode = "unknown"
        has_transparency = False
        
        # PNG analysis
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            format_detected = "png"
            # PNG dimensions are at bytes 16-24
            if len(image_data) >= 24:
                width = int.from_bytes(image_data[16:20], 'big')
                height = int.from_bytes(image_data[20:24], 'big')
            # Check for transparency in IHDR color type
            if len(image_data) >= 26:
                color_type = image_data[25]
                has_transparency = color_type in (4, 6)
                color_mode = {0: "grayscale", 2: "RGB", 3: "indexed", 4: "grayscale+alpha", 6: "RGBA"}.get(color_type, "unknown")
        
        # JPEG analysis
        elif image_data[:2] == b'\xff\xd8':
            format_detected = "jpeg"
            color_mode = "RGB"
            # Find SOF0 marker for dimensions
            i = 2
            while i < len(image_data) - 9:
                if image_data[i] == 0xff:
                    marker = image_data[i + 1]
                    if marker in (0xc0, 0xc2):  # SOF0 or SOF2
                        height = int.from_bytes(image_data[i + 5:i + 7], 'big')
                        width = int.from_bytes(image_data[i + 7:i + 9], 'big')
                        break
                    elif marker == 0xd9:  # EOI
                        break
                    else:
                        length = int.from_bytes(image_data[i + 2:i + 4], 'big')
                        i += length + 2
                else:
                    i += 1
        
        # GIF analysis
        elif image_data[:6] in (b'GIF87a', b'GIF89a'):
            format_detected = "gif"
            if len(image_data) >= 10:
                width = int.from_bytes(image_data[6:8], 'little')
                height = int.from_bytes(image_data[8:10], 'little')
            color_mode = "indexed"
            has_transparency = True  # GIF supports transparency
        
        return ImageAnalysis(
            format=format_detected,
            width=width,
            height=height,
            color_mode=color_mode,
            file_size=len(image_data),
            has_transparency=has_transparency,
            confidence=0.8 if format_detected != "unknown" else 0.3
        )
    
    @staticmethod
    def get_image_description(analysis: ImageAnalysis) -> str:
        """Generate a text description of the image"""
        parts = []
        
        if analysis.format != "unknown":
            parts.append(f"Format: {analysis.format.upper()}")
        
        if analysis.width > 0 and analysis.height > 0:
            parts.append(f"Dimensions: {analysis.width}x{analysis.height} pixels")
        
        if analysis.color_mode != "unknown":
            parts.append(f"Color mode: {analysis.color_mode}")
        
        if analysis.has_transparency:
            parts.append("Has transparency")
        
        parts.append(f"File size: {analysis.file_size:,} bytes")
        
        return "; ".join(parts)


class AudioHandler:
    """
    Handles audio processing and analysis
    
    Note: For full audio processing, libraries like pydub or librosa would be required.
    This implementation provides basic functionality without external dependencies.
    """
    
    @staticmethod
    def load_audio(file_path: str) -> Optional[MultimodalContent]:
        """Load an audio file"""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Audio file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            content_id = hashlib.sha256(data).hexdigest()[:16]
            mime_type = ContentDetector.get_mime_type(file_path)
            
            return MultimodalContent(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                data=data,
                mime_type=mime_type,
                metadata={
                    "filename": path.name,
                    "file_size": len(data)
                },
                source=file_path
            )
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            return None
    
    @staticmethod
    def analyze_audio(audio_data: bytes) -> AudioAnalysis:
        """
        Analyze audio properties
        
        Note: This is a basic implementation. Full analysis would require
        audio processing libraries.
        """
        format_detected = "unknown"
        duration_seconds = 0.0
        sample_rate = 0
        channels = 0
        bitrate = 0
        
        # WAV analysis
        if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            format_detected = "wav"
            if len(audio_data) >= 44:
                channels = int.from_bytes(audio_data[22:24], 'little')
                sample_rate = int.from_bytes(audio_data[24:28], 'little')
                byte_rate = int.from_bytes(audio_data[28:32], 'little')
                bitrate = byte_rate * 8
                
                # Find data chunk size
                i = 12
                while i < len(audio_data) - 8:
                    chunk_id = audio_data[i:i+4]
                    chunk_size = int.from_bytes(audio_data[i+4:i+8], 'little')
                    if chunk_id == b'data':
                        if byte_rate > 0:
                            duration_seconds = chunk_size / byte_rate
                        break
                    i += 8 + chunk_size
        
        # MP3 analysis (basic)
        elif audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
            format_detected = "mp3"
            # Rough estimate based on file size and typical bitrate
            bitrate = 128000  # Assume 128kbps
            duration_seconds = len(audio_data) * 8 / bitrate
        
        # OGG/Vorbis analysis
        elif audio_data[:4] == b'OggS':
            format_detected = "ogg"
        
        # FLAC analysis
        elif audio_data[:4] == b'fLaC':
            format_detected = "flac"
            if len(audio_data) >= 26:
                # STREAMINFO metadata block
                sample_rate = (audio_data[18] << 12) | (audio_data[19] << 4) | (audio_data[20] >> 4)
                channels = ((audio_data[20] >> 1) & 0x7) + 1
        
        return AudioAnalysis(
            format=format_detected,
            duration_seconds=round(duration_seconds, 2),
            sample_rate=sample_rate,
            channels=channels,
            bitrate=bitrate,
            file_size=len(audio_data)
        )
    
    @staticmethod
    def get_audio_description(analysis: AudioAnalysis) -> str:
        """Generate a text description of the audio"""
        parts = []
        
        if analysis.format != "unknown":
            parts.append(f"Format: {analysis.format.upper()}")
        
        if analysis.duration_seconds > 0:
            minutes = int(analysis.duration_seconds // 60)
            seconds = int(analysis.duration_seconds % 60)
            parts.append(f"Duration: {minutes}:{seconds:02d}")
        
        if analysis.sample_rate > 0:
            parts.append(f"Sample rate: {analysis.sample_rate} Hz")
        
        if analysis.channels > 0:
            channel_desc = "Mono" if analysis.channels == 1 else f"{analysis.channels} channels"
            parts.append(f"Channels: {channel_desc}")
        
        if analysis.bitrate > 0:
            parts.append(f"Bitrate: {analysis.bitrate // 1000} kbps")
        
        parts.append(f"File size: {analysis.file_size:,} bytes")
        
        return "; ".join(parts)


class MultimodalProcessor:
    """
    Main processor for handling multimodal content
    
    Integrates image and audio handling with content detection
    """
    
    def __init__(self):
        self.content_cache: Dict[str, MultimodalContent] = {}
        self.image_handler = ImageHandler()
        self.audio_handler = AudioHandler()
        
        logger.info("🎨 Multimodal Processor initialized")
    
    def load_content(self, file_path: str) -> Optional[MultimodalContent]:
        """Load content from file, detecting type automatically"""
        content_type = ContentDetector.detect_from_path(file_path)
        
        if content_type == ContentType.IMAGE:
            content = self.image_handler.load_image(file_path)
        elif content_type == ContentType.AUDIO:
            content = self.audio_handler.load_audio(file_path)
        elif content_type == ContentType.TEXT:
            content = self._load_text(file_path)
        else:
            content = self._load_binary(file_path)
        
        if content:
            self.content_cache[content.content_id] = content
            logger.info(f"📁 Loaded {content_type.value}: {file_path}")
        
        return content
    
    def _load_text(self, file_path: str) -> Optional[MultimodalContent]:
        """Load text content from file"""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            content_id = hashlib.sha256(data.encode()).hexdigest()[:16]
            
            return MultimodalContent(
                content_id=content_id,
                content_type=ContentType.TEXT,
                data=data,
                mime_type="text/plain",
                metadata={
                    "filename": path.name,
                    "char_count": len(data),
                    "line_count": data.count('\n') + 1
                },
                source=file_path
            )
        except Exception as e:
            logger.error(f"Error loading text: {e}")
            return None
    
    def _load_binary(self, file_path: str) -> Optional[MultimodalContent]:
        """Load binary content from file"""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            content_id = hashlib.sha256(data).hexdigest()[:16]
            mime_type = ContentDetector.get_mime_type(file_path)
            content_type = ContentDetector.detect_from_bytes(data)
            
            return MultimodalContent(
                content_id=content_id,
                content_type=content_type,
                data=data,
                mime_type=mime_type,
                metadata={
                    "filename": path.name,
                    "file_size": len(data)
                },
                source=file_path
            )
        except Exception as e:
            logger.error(f"Error loading binary: {e}")
            return None
    
    def analyze_content(self, content: MultimodalContent) -> Dict[str, Any]:
        """Analyze content based on its type"""
        if content.content_type == ContentType.IMAGE:
            analysis = self.image_handler.analyze_image(content.data)
            return {
                "type": "image",
                "analysis": analysis.__dict__,
                "description": self.image_handler.get_image_description(analysis)
            }
        elif content.content_type == ContentType.AUDIO:
            analysis = self.audio_handler.analyze_audio(content.data)
            return {
                "type": "audio",
                "analysis": analysis.__dict__,
                "description": self.audio_handler.get_audio_description(analysis)
            }
        elif content.content_type == ContentType.TEXT:
            text = content.data if isinstance(content.data, str) else content.data.decode('utf-8')
            return {
                "type": "text",
                "analysis": {
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "line_count": text.count('\n') + 1
                },
                "description": f"Text document with {len(text.split())} words"
            }
        else:
            return {
                "type": content.content_type.value,
                "analysis": content.metadata,
                "description": f"{content.content_type.value} content"
            }
    
    def get_content_description(self, content: MultimodalContent) -> str:
        """Get a human-readable description of content"""
        analysis = self.analyze_content(content)
        return analysis.get("description", "Unknown content")
    
    def convert_to_base64(self, content: MultimodalContent) -> str:
        """Convert content to base64 for transmission"""
        if isinstance(content.data, bytes):
            return base64.b64encode(content.data).decode('utf-8')
        else:
            return base64.b64encode(content.data.encode('utf-8')).decode('utf-8')
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported formats by content type"""
        return {
            "image": ["jpeg", "png", "gif", "webp", "bmp", "svg"],
            "audio": ["mp3", "wav", "ogg", "flac", "m4a", "aac"],
            "video": ["mp4", "webm", "mov", "avi"],
            "document": ["pdf", "doc", "docx"],
            "text": ["txt", "md", "html"],
            "code": ["py", "js", "ts", "java", "cpp", "c", "go", "rs", "json", "yaml"]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        type_counts = {}
        for content in self.content_cache.values():
            type_name = content.content_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "cached_items": len(self.content_cache),
            "by_type": type_counts,
            "supported_formats": self.get_supported_formats()
        }


# Convenience function to create processor
def create_multimodal_processor() -> MultimodalProcessor:
    """Create a new multimodal processor instance"""
    return MultimodalProcessor()


# ==================== MAIN ====================

def main():
    """Demo the multimodal support"""
    print("=" * 60)
    print("🎨 THE FORGE AI - Multimodal Support Demo")
    print("=" * 60)
    print()
    
    # Initialize processor
    processor = MultimodalProcessor()
    
    # Demo: Content type detection
    print("📁 Demo: Content Type Detection")
    print("-" * 40)
    test_paths = [
        "image.png",
        "audio.mp3",
        "document.pdf",
        "script.py",
        "data.json"
    ]
    for path in test_paths:
        content_type = ContentDetector.detect_from_path(path)
        mime_type = ContentDetector.get_mime_type(path)
        print(f"  {path} → {content_type.value} ({mime_type})")
    print()
    
    # Demo: Supported formats
    print("📋 Demo: Supported Formats")
    print("-" * 40)
    formats = processor.get_supported_formats()
    for category, format_list in formats.items():
        print(f"  {category}: {', '.join(format_list)}")
    print()
    
    # Demo: Image analysis (with sample data)
    print("🖼️ Demo: Image Analysis")
    print("-" * 40)
    # Create a minimal PNG for testing
    sample_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D,  # IHDR length
        0x49, 0x48, 0x44, 0x52,  # IHDR
        0x00, 0x00, 0x00, 0x64,  # width: 100
        0x00, 0x00, 0x00, 0x64,  # height: 100
        0x08, 0x02,  # bit depth: 8, color type: 2 (RGB)
        0x00, 0x00, 0x00,  # compression, filter, interlace
    ])
    analysis = ImageHandler.analyze_image(sample_png)
    print(f"  Format: {analysis.format}")
    print(f"  Dimensions: {analysis.width}x{analysis.height}")
    print(f"  Color Mode: {analysis.color_mode}")
    print(f"  Has Transparency: {analysis.has_transparency}")
    print()
    
    # Demo: Audio analysis (with sample data)
    print("🔊 Demo: Audio Analysis")
    print("-" * 40)
    # Create minimal WAV header for testing
    sample_wav = bytes([
        0x52, 0x49, 0x46, 0x46,  # RIFF
        0x00, 0x00, 0x00, 0x00,  # file size (placeholder)
        0x57, 0x41, 0x56, 0x45,  # WAVE
        0x66, 0x6D, 0x74, 0x20,  # fmt
        0x10, 0x00, 0x00, 0x00,  # chunk size
        0x01, 0x00,  # audio format (PCM)
        0x02, 0x00,  # channels: 2
        0x44, 0xAC, 0x00, 0x00,  # sample rate: 44100
        0x10, 0xB1, 0x02, 0x00,  # byte rate
        0x04, 0x00,  # block align
        0x10, 0x00,  # bits per sample
    ])
    analysis = AudioHandler.analyze_audio(sample_wav)
    print(f"  Format: {analysis.format}")
    print(f"  Sample Rate: {analysis.sample_rate} Hz")
    print(f"  Channels: {analysis.channels}")
    print()
    
    # Demo: Statistics
    print("📊 Demo: Processor Statistics")
    print("-" * 40)
    stats = processor.get_stats()
    print(f"  Cached items: {stats['cached_items']}")
    print(f"  Supported format categories: {len(stats['supported_formats'])}")
    
    print("\n" + "=" * 60)
    print("✅ Multimodal Support Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
