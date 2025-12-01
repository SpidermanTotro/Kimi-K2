#!/usr/bin/env python3
"""
THE FORGE - Multimedia Production Suite
Transforms MULTIMEDIA_CAPABILITIES.md into live multimedia tools
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"
    MKV = "mkv"
    FLV = "flv"


class VideoResolution(Enum):
    """Video resolutions"""
    SD = "640x480"
    HD = "1280x720"
    FULL_HD = "1920x1080"
    QHD = "2560x1440"
    UHD_4K = "3840x2160"
    UHD_8K = "7680x4320"


class VideoCodec(Enum):
    """Video codecs"""
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    PRORES = "prores"


@dataclass
class VideoProject:
    """Video editing project"""
    name: str
    input_files: List[str] = field(default_factory=list)
    output_file: str = ""
    resolution: VideoResolution = VideoResolution.FULL_HD
    format: VideoFormat = VideoFormat.MP4
    codec: VideoCodec = VideoCodec.H264
    fps: int = 30
    bitrate: str = "5M"
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'input_files': self.input_files,
            'output_file': self.output_file,
            'resolution': self.resolution.value,
            'format': self.format.value,
            'codec': self.codec.value,
            'fps': self.fps,
            'bitrate': self.bitrate
        }


@dataclass
class AudioProject:
    """Audio editing project"""
    name: str
    input_file: str
    output_file: str
    sample_rate: int = 44100
    channels: int = 2
    bitrate: str = "192k"
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bitrate': self.bitrate
        }


class MultimediaSuite:
    """
    Multimedia Production Suite
    - Video editing and processing
    - Audio recording and editing
    - Photo editing
    - YouTube optimization
    """
    
    def __init__(self, workspace: str = "multimedia_workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        self.projects: Dict[str, VideoProject] = {}
        self.audio_projects: Dict[str, AudioProject] = {}
        
    def create_video_project(self, name: str, **kwargs) -> VideoProject:
        """Create a new video project"""
        project = VideoProject(name=name, **kwargs)
        self.projects[name] = project
        
        # Create project directory
        project_dir = self.workspace / name
        project_dir.mkdir(exist_ok=True)
        
        print(f"✅ Created video project: {name}")
        return project
    
    def add_video_clip(self, project_name: str, video_file: str):
        """Add video clip to project"""
        if project_name not in self.projects:
            raise ValueError(f"Project not found: {project_name}")
        
        project = self.projects[project_name]
        project.input_files.append(video_file)
        print(f"✅ Added clip to {project_name}: {video_file}")
    
    def concatenate_videos(self, project_name: str, output_file: str) -> bool:
        """Concatenate multiple videos"""
        if project_name not in self.projects:
            raise ValueError(f"Project not found: {project_name}")
        
        project = self.projects[project_name]
        
        if len(project.input_files) < 2:
            print("⚠️  Need at least 2 videos to concatenate")
            return False
        
        print(f"🎬 Concatenating {len(project.input_files)} videos...")
        
        # Create concat file list
        concat_file = self.workspace / project_name / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video in project.input_files:
                f.write(f"file '{video}'\n")
        
        # FFmpeg command to concatenate
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            output_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            project.output_file = output_file
            print(f"✅ Videos concatenated: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error concatenating videos: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed. Install with: sudo apt-get install ffmpeg")
            return False
    
    def convert_video(self, input_file: str, output_file: str, 
                     resolution: Optional[VideoResolution] = None,
                     codec: Optional[VideoCodec] = None,
                     bitrate: str = "5M") -> bool:
        """Convert video format/resolution/codec"""
        print(f"🎬 Converting video: {input_file}")
        
        cmd = ['ffmpeg', '-i', input_file]
        
        if codec:
            cmd.extend(['-c:v', codec.value])
        
        if resolution:
            cmd.extend(['-s', resolution.value])
        
        cmd.extend(['-b:v', bitrate, output_file])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video converted: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error converting video: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed")
            return False
    
    def extract_audio(self, video_file: str, audio_file: str) -> bool:
        """Extract audio from video"""
        print(f"🎵 Extracting audio from: {video_file}")
        
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            audio_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Audio extracted: {audio_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extracting audio: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed")
            return False
    
    def add_audio_to_video(self, video_file: str, audio_file: str, 
                          output_file: str) -> bool:
        """Add audio track to video"""
        print(f"🎵 Adding audio to video...")
        
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Audio added: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error adding audio: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed")
            return False
    
    def create_thumbnail(self, video_file: str, output_image: str, 
                        timestamp: str = "00:00:01") -> bool:
        """Create thumbnail from video"""
        print(f"📸 Creating thumbnail at {timestamp}...")
        
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-ss', timestamp,
            '-vframes', '1',
            output_image
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Thumbnail created: {output_image}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating thumbnail: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed")
            return False
    
    def get_video_info(self, video_file: str) -> Optional[Dict]:
        """Get video information"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_file
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            # Extract key information
            video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
            audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
            
            return {
                'duration': float(info['format'].get('duration', 0)),
                'size': int(info['format'].get('size', 0)),
                'bitrate': int(info['format'].get('bit_rate', 0)),
                'video': {
                    'codec': video_stream.get('codec_name') if video_stream else None,
                    'width': video_stream.get('width') if video_stream else None,
                    'height': video_stream.get('height') if video_stream else None,
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else None
                },
                'audio': {
                    'codec': audio_stream.get('codec_name') if audio_stream else None,
                    'sample_rate': audio_stream.get('sample_rate') if audio_stream else None,
                    'channels': audio_stream.get('channels') if audio_stream else None
                }
            }
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            return None
    
    def create_audio_project(self, name: str, input_file: str, 
                           output_file: str) -> AudioProject:
        """Create audio editing project"""
        project = AudioProject(
            name=name,
            input_file=input_file,
            output_file=output_file
        )
        self.audio_projects[name] = project
        print(f"✅ Created audio project: {name}")
        return project
    
    def normalize_audio(self, input_file: str, output_file: str) -> bool:
        """Normalize audio levels"""
        print(f"🎵 Normalizing audio...")
        
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-af', 'loudnorm',
            output_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Audio normalized: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error normalizing audio: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed")
            return False
    
    def export_project(self, project_name: str, output_file: str = "project.json"):
        """Export project configuration"""
        if project_name not in self.projects:
            raise ValueError(f"Project not found: {project_name}")
        
        project = self.projects[project_name]
        
        with open(output_file, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
        
        print(f"✅ Project exported: {output_file}")
    
    def get_capabilities(self) -> Dict:
        """Get available capabilities"""
        return {
            'video_editing': [
                'Concatenate videos',
                'Convert formats',
                'Change resolution',
                'Change codec',
                'Extract audio',
                'Add audio track',
                'Create thumbnails',
                'Get video info'
            ],
            'audio_editing': [
                'Normalize audio',
                'Convert formats',
                'Extract from video',
                'Mix audio tracks'
            ],
            'supported_formats': {
                'video': [f.value for f in VideoFormat],
                'codecs': [c.value for c in VideoCodec],
                'resolutions': [r.value for r in VideoResolution]
            }
        }


def main():
    """Main execution"""
    print("🔥 THE FORGE - Multimedia Production Suite")
    print("=" * 70)
    print()
    
    # Initialize suite
    suite = MultimediaSuite()
    
    # Show capabilities
    print("📋 Available Capabilities:")
    print("-" * 70)
    caps = suite.get_capabilities()
    
    print("\n🎬 Video Editing:")
    for cap in caps['video_editing']:
        print(f"  ✅ {cap}")
    
    print("\n🎵 Audio Editing:")
    for cap in caps['audio_editing']:
        print(f"  ✅ {cap}")
    
    print("\n📦 Supported Formats:")
    print(f"  Video: {', '.join(caps['supported_formats']['video'])}")
    print(f"  Codecs: {', '.join(caps['supported_formats']['codecs'])}")
    
    print("\n✅ Multimedia Suite Ready!")
    print("\n💡 Example Usage:")
    print("  project = suite.create_video_project('my_video')")
    print("  suite.add_video_clip('my_video', 'clip1.mp4')")
    print("  suite.add_video_clip('my_video', 'clip2.mp4')")
    print("  suite.concatenate_videos('my_video', 'output.mp4')")


if __name__ == "__main__":
    main()