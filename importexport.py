#!/usr/bin/env python3
"""
DaVinci Resolve OTIO Import/Export Script

This script provides an interactive terminal interface for:
1. Exporting the currently open timeline from DaVinci Resolve to OTIO format
2. Importing OTIO files into DaVinci Resolve as new timelines

Requirements:
- DaVinci Resolve must be running
- Python 3.6+ (64-bit)
- Proper DaVinci Resolve API environment setup
- A project must be open in DaVinci Resolve
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Optional, Dict, Any


class ResolveConnection:
    """Handles connection to DaVinci Resolve and API setup."""
    
    def __init__(self):
        self.resolve = None
        self.project_manager = None
        self.current_project = None
        self.current_timeline = None
        self._setup_environment()
        
    def _setup_environment(self):
        """Set up DaVinci Resolve API environment variables and paths."""
        print("Setting up DaVinci Resolve API environment...")
        
        # Check Python version and architecture
        if sys.maxsize <= 2**32:
            raise RuntimeError("DaVinci Resolve requires 64-bit Python!")
        
        # Set platform-specific paths
        if sys.platform.startswith("win"):
            resolve_script_api = os.path.join(
                os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                "Blackmagic Design", "DaVinci Resolve", "Support", 
                "Developer", "Scripting"
            )
            resolve_script_lib = os.path.join(
                os.environ.get("PROGRAMFILES", "C:\\Program Files"), 
                "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll"
            )
        elif sys.platform.startswith("darwin"):
            resolve_script_api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
            resolve_script_lib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
        else:  # Linux
            resolve_script_api = "/opt/resolve/Developer/Scripting"
            resolve_script_lib = "/opt/resolve/libs/Fusion/fusionscript.so"
        
        # Set environment variables
        os.environ["RESOLVE_SCRIPT_API"] = resolve_script_api
        os.environ["RESOLVE_SCRIPT_LIB"] = resolve_script_lib
        
        # Add modules to Python path
        modules_path = os.path.join(resolve_script_api, "Modules")
        if not os.path.isdir(modules_path):
            raise RuntimeError(f"Resolve scripting modules path does not exist: {modules_path}")
        
        if modules_path not in sys.path:
            sys.path.append(modules_path)
        
        print(f"✓ API modules path: {modules_path}")
    
    def connect(self):
        """Establish connection to DaVinci Resolve."""
        print("Connecting to DaVinci Resolve...")
        
        try:
            import DaVinciResolveScript as dvr_script
            self.resolve = dvr_script.scriptapp("Resolve")
            
            if not self.resolve:
                raise RuntimeError("Failed to connect to Resolve. Make sure Resolve is running.")
            
            self.project_manager = self.resolve.GetProjectManager()
            self.current_project = self.project_manager.GetCurrentProject()
            
            if not self.current_project:
                raise RuntimeError("No project is currently open. Please open a project in DaVinci Resolve.")
            
            self.current_timeline = self.current_project.GetCurrentTimeline()
            
            # Print connection info
            version = self.resolve.GetVersionString()
            project_name = self.current_project.GetName()
            
            print(f"✓ Connected to DaVinci Resolve {version}")
            print(f"✓ Current project: {project_name}")
            
            if self.current_timeline:
                timeline_name = self.current_timeline.GetName()
                start_frame = self.current_timeline.GetStartFrame()
                end_frame = self.current_timeline.GetEndFrame()
                duration = end_frame - start_frame + 1
                print(f"✓ Current timeline: {timeline_name} (frames {start_frame}-{end_frame}, duration: {duration})")
            else:
                print("⚠ No timeline is currently open")
            
            return True
            
        except ImportError as e:
            raise RuntimeError(f"Failed to import DaVinciResolveScript: {e}")
        except Exception as e:
            raise RuntimeError(f"Connection error: {e}")
    
    def ensure_timeline(self):
        """Ensure a timeline is open."""
        if not self.current_timeline:
            raise RuntimeError("No timeline is currently open. Please open a timeline in DaVinci Resolve.")


class OTIOManager:
    """Handles OTIO export and import functionality."""
    
    def __init__(self, connection: ResolveConnection):
        self.connection = connection
    
    def export_current_timeline(self, output_path: str) -> bool:
        """
        Export the currently open timeline to OTIO format.
        
        Args:
            output_path: Path where the OTIO file should be saved
            
        Returns:
            True if export successful, False otherwise
        """
        self.connection.ensure_timeline()
        
        timeline = self.connection.current_timeline
        timeline_name = timeline.GetName()
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure .otio extension
        if output_path.suffix.lower() != '.otio':
            output_path = output_path.with_suffix('.otio')
        
        print(f"\nExporting timeline '{timeline_name}' to: {output_path}")
        
        try:
            # Export using OTIO format
            success = timeline.Export(str(output_path), self.connection.resolve.EXPORT_OTIO, self.connection.resolve.EXPORT_NONE)
            
            if success:
                print(f"✓ Successfully exported timeline to {output_path}")
                return True
            else:
                raise RuntimeError("Export operation failed")
                
        except Exception as e:
            raise RuntimeError(f"Failed to export timeline: {e}")
    
    def import_otio(self, otio_file_path: str, timeline_name: Optional[str] = None) -> bool:
        """
        Import an OTIO file as a new timeline in DaVinci Resolve.
        
        Args:
            otio_file_path: Path to the OTIO file to import
            timeline_name: Optional name for the new timeline (defaults to filename)
            
        Returns:
            True if import successful, False otherwise
        """
        # Validate file
        otio_path = Path(otio_file_path)
        if not otio_path.exists():
            raise FileNotFoundError(f"OTIO file not found: {otio_file_path}")
        
        if otio_path.suffix.lower() != '.otio':
            raise ValueError(f"File must have .otio extension: {otio_file_path}")
        
        # Generate timeline name if not provided
        if not timeline_name:
            timeline_name = otio_path.stem
        
        print(f"\nImporting OTIO file: {otio_path}")
        print(f"Creating new timeline: {timeline_name}")
        print(f"File size: {otio_path.stat().st_size} bytes")
        
        try:
            # Get media pool
            media_pool = self.connection.current_project.GetMediaPool()
            if not media_pool:
                raise RuntimeError("Failed to get media pool")
            
            # Import OTIO as a new timeline
            import_options = {
                'timelineName': timeline_name,
                'importSourceClips': True,
                'sourceClipsPath': str(otio_path.parent),
                'sourceClipsFolders': [],  # Will search current media pool
                'interlaceProcessing': False
            }
            
            print("Creating timeline from OTIO...")
            print(f"Using source clips path: {otio_path.parent}")
            
            # First, try to import any media files in the source directory to media pool
            print("Pre-importing media files to media pool...")
            self._preimport_media_files(otio_path.parent)
            
            new_timeline = media_pool.ImportTimelineFromFile(str(otio_path), import_options)
            
            if not new_timeline:
                # Try with different options if first attempt fails
                print("First import attempt failed, trying with different options...")
                import_options = {
                    'timelineName': timeline_name,
                    'importSourceClips': False,  # Don't try to import source clips
                    'interlaceProcessing': False
                }
                new_timeline = media_pool.ImportTimelineFromFile(str(otio_path), import_options)
            
            if not new_timeline:
                # Try without any import options
                print("Second import attempt failed, trying with minimal options...")
                new_timeline = media_pool.ImportTimelineFromFile(str(otio_path), {})
            
            if not new_timeline:
                raise RuntimeError("Failed to import OTIO file - all import attempts failed. The OTIO file may be corrupted or incompatible.")
            
            print("✓ Timeline created successfully")
            
            # Set the new timeline as current
            self.connection.current_project.SetCurrentTimeline(new_timeline)
            self.connection.current_timeline = new_timeline  # Update our reference
            
            # Get timeline information
            video_tracks = new_timeline.GetTrackCount('video')
            audio_tracks = new_timeline.GetTrackCount('audio')
            start_frame = new_timeline.GetStartFrame()
            end_frame = new_timeline.GetEndFrame()
            
            print(f"\nTimeline info:")
            print(f"  Name: {timeline_name}")
            print(f"  Video tracks: {video_tracks}")
            print(f"  Audio tracks: {audio_tracks}")
            print(f"  Frame range: {start_frame} to {end_frame}")
            
            # Count timeline items for reporting
            total_items = 0
            media_items = 0
            
            for track_idx in range(1, video_tracks + 1):
                track_items = new_timeline.GetItemListInTrack('video', track_idx)
                total_items += len(track_items)
                for item in track_items:
                    if item.GetMediaPoolItem():
                        media_items += 1
            
            for track_idx in range(1, audio_tracks + 1):
                track_items = new_timeline.GetItemListInTrack('audio', track_idx)
                total_items += len(track_items)
                for item in track_items:
                    if item.GetMediaPoolItem():
                        media_items += 1
            
            print(f"  Total timeline items: {total_items}")
            print(f"  Media-based items: {media_items}")
            print(f"  Generated/effect items: {total_items - media_items}")
            
            # Try to relink any offline clips
            print(f"\nChecking for offline clips and attempting relink...")
            self._relink_offline_clips(new_timeline, otio_path.parent)
            
            print(f"\n✓ Successfully imported OTIO as timeline '{timeline_name}'")
            print(f"✓ Timeline set as current timeline")
            
            return True
                
        except Exception as e:
            raise RuntimeError(f"Failed to import OTIO file: {e}")
    
    def _relink_offline_clips(self, timeline, source_path):
        """Attempt to relink any offline clips in the timeline."""
        try:
            media_pool = self.connection.current_project.GetMediaPool()
            
            # Collect all timeline items that might need relinking
            offline_items = []
            video_tracks = timeline.GetTrackCount('video')
            audio_tracks = timeline.GetTrackCount('audio')
            
            # Check video tracks
            for track_idx in range(1, video_tracks + 1):
                track_items = timeline.GetItemListInTrack('video', track_idx)
                for item in track_items:
                    mp_item = item.GetMediaPoolItem()
                    if mp_item:
                        # Check if the clip appears to be offline (this is a heuristic)
                        clip_name = mp_item.GetName()
                        if "Media Offline" in clip_name or not mp_item.GetClipProperty("File Path"):
                            offline_items.append(mp_item)
            
            # Check audio tracks
            for track_idx in range(1, audio_tracks + 1):
                track_items = timeline.GetItemListInTrack('audio', track_idx)
                for item in track_items:
                    mp_item = item.GetMediaPoolItem()
                    if mp_item:
                        clip_name = mp_item.GetName()
                        if "Media Offline" in clip_name or not mp_item.GetClipProperty("File Path"):
                            offline_items.append(mp_item)
            
            if offline_items:
                print(f"Found {len(offline_items)} potentially offline clips")
                print("Attempting to relink clips...")
                
                # Try to relink clips to source folder
                success = media_pool.RelinkClips(offline_items, str(source_path))
                if success:
                    print("✓ Successfully relinked offline clips")
                else:
                    print("⚠ Relink attempt completed (some clips may still be offline)")
                    
                # Alternative approach: try reconform from bins
                print("Attempting timeline reconform...")
                try:
                    # Note: This method may not be available in all versions
                    timeline_reconform_success = timeline.ImportIntoTimeline(
                        "", {
                            'autoImportSourceClipsIntoMediaPool': True,
                            'sourceClipsPath': str(source_path)
                        }
                    )
                    if timeline_reconform_success:
                        print("✓ Timeline reconform successful")
                except Exception as reconform_error:
                    print(f"⚠ Timeline reconform not available: {reconform_error}")
            else:
                print("✓ No offline clips detected")
                
        except Exception as e:
            print(f"⚠ Error during relink attempt: {e}")
            print("You may need to manually relink clips using 'Conform Lock with Media Pool Clip'")
    
    def _preimport_media_files(self, source_path):
        """Pre-import media files from source directory to improve linking."""
        try:
            media_storage = self.connection.resolve.GetMediaStorage()
            media_pool = self.connection.current_project.GetMediaPool()
            
            if not media_storage or not media_pool:
                print("⚠ Could not access media storage or media pool")
                return
            
            # Get list of media files in the source directory
            source_dir = Path(source_path)
            if not source_dir.exists():
                print(f"⚠ Source directory does not exist: {source_path}")
                return
            
            # Common video/audio file extensions
            media_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.mxf', '.r3d', '.braw', 
                              '.wav', '.aiff', '.mp3', '.m4a', '.flac',
                              '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.exr', '.dpx'}
            
            media_files = []
            for file_path in source_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                    media_files.append(str(file_path))
            
            if media_files:
                print(f"Found {len(media_files)} media files to pre-import")
                # Import media files to media pool
                imported_items = media_pool.ImportMedia(media_files)
                if imported_items:
                    print(f"✓ Pre-imported {len(imported_items)} media files")
                else:
                    print("⚠ Media pre-import completed (some files may not have imported)")
            else:
                print("No media files found in source directory")
                
        except Exception as e:
            print(f"⚠ Error during media pre-import: {e}")


def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def export_menu(otio_manager: OTIOManager):
    """Handle export functionality with user interaction."""
    print("\n" + "="*50)
    print("EXPORT CURRENT TIMELINE TO OTIO")
    print("="*50)
    
    try:
        # Check if there's a current timeline
        if not otio_manager.connection.current_timeline:
            print("❌ No timeline is currently open. Please open a timeline in DaVinci Resolve.")
            return
        
        timeline = otio_manager.connection.current_timeline
        timeline_name = timeline.GetName()
        
        if not timeline_name or timeline_name == "None":
            print("❌ Unable to get timeline name. Please ensure a timeline is properly loaded.")
            return
        
        print(f"Current timeline: {timeline_name}")
        
        # Automatically set output path to data folder
        data_folder = Path("D:/Git/davinciapitest/data")
        output_path = data_folder / f"{timeline_name}.otio"
        
        print(f"Export location: {output_path}")
        
        # Simple confirmation
        confirm = get_user_input(f"Export '{timeline_name}' to data folder? (y/n)", "y").lower()
        if confirm not in ['y', 'yes']:
            print("Export cancelled")
            return
        
        # Perform export
        success = otio_manager.export_current_timeline(str(output_path))
        if success:
            print(f"\n✓ Export completed successfully!")
            print(f"✓ File saved: {output_path}")
        else:
            print(f"\n❌ Export failed!")
            
    except Exception as e:
        print(f"\n❌ Export error: {e}")


def import_menu(otio_manager: OTIOManager):
    """Handle import functionality with user interaction."""
    print("\n" + "="*50)
    print("IMPORT OTIO FILE AS NEW TIMELINE")
    print("="*50)
    
    try:
        # Get full path to OTIO file directly
        otio_file_path = get_user_input("Enter full path to OTIO file")
        
        if not otio_file_path:
            print("❌ No file path provided")
            return
        
        # Validate the file path
        otio_path = Path(otio_file_path)
        
        if not otio_path.exists():
            print(f"❌ File not found: {otio_file_path}")
            return
        
        if otio_path.suffix.lower() != '.otio':
            print(f"❌ File must have .otio extension. Found: {otio_path.suffix}")
            return
        
        print(f"✓ Found OTIO file: {otio_path.name}")
        
        # Get timeline name
        default_name = otio_path.stem
        timeline_name = get_user_input("Enter name for new timeline", default_name)
        
        if not timeline_name:
            print("❌ No timeline name provided")
            return
        
        # Confirm import
        confirm = get_user_input(f"Import '{otio_path.name}' as new timeline '{timeline_name}'? (y/n)", "y").lower()
        if confirm not in ['y', 'yes']:
            print("Import cancelled")
            return
        
        # Perform import
        success = otio_manager.import_otio(str(otio_path), timeline_name)
        if success:
            print(f"\n✓ Import completed successfully!")
        else:
            print(f"\n❌ Import failed!")
            
    except Exception as e:
        print(f"\n❌ Import error: {e}")


def main_menu():
    """Display and handle the main menu."""
    print("\n" + "="*50)
    print("DAVINCI RESOLVE OTIO IMPORT/EXPORT TOOL")
    print("="*50)
    
    try:
        # Establish connection
        print("Initializing connection to DaVinci Resolve...")
        connection = ResolveConnection()
        connection.connect()
        
        otio_manager = OTIOManager(connection)
        
        print("\n✓ Connection established successfully!")
        
        # Main menu loop
        while True:
            print("\n" + "-"*30)
            print("MAIN MENU")
            print("-"*30)
            print("1. Export current timeline to OTIO")
            print("2. Import OTIO file as new timeline")
            print("3. Quit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                if connection.current_timeline:
                    export_menu(otio_manager)
                else:
                    print("❌ No timeline is currently open. Please open a timeline in DaVinci Resolve.")
            elif choice == '2':
                import_menu(otio_manager)
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("- DaVinci Resolve is running")
        print("- A project is open in DaVinci Resolve")
        print("- Python is 64-bit")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main_menu())
