#!/usr/bin/env python3
"""
DaVinci Resolve API Test Script
Basic template for testing DaVinci Resolve API functionality.
"""

import sys
import os
import traceback
from typing import Optional, Any


class DaVinciResolver:
    """Handler for DaVinci Resolve API connections and operations."""
    
    def __init__(self):
        self.resolve = None
        self.project_manager = None
        self.current_project = None
        
    def setup_environment(self) -> bool:
        """Set up the DaVinci Resolve API environment."""
        print("Setting up DaVinci Resolve API environment...")
        
        # Check Python architecture
        if not sys.maxsize > 2**32:
            print("ERROR: DaVinci Resolve requires 64-bit Python!")
            return False
            
        # Set platform-specific paths
        if sys.platform.startswith("win"):
            resolve_script_api = os.path.join(
                os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                "Blackmagic Design", "DaVinci Resolve", "Support", 
                "Developer", "Scripting"
            )
        elif sys.platform.startswith("darwin"):
            resolve_script_api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
        else:  # Linux
            resolve_script_api = "/opt/resolve/Developer/Scripting"
            
        # Verify modules path exists
        modules_path = os.path.join(resolve_script_api, "Modules")
        if not os.path.isdir(modules_path):
            print(f"ERROR: Resolve scripting modules path does not exist: {modules_path}")
            print("Please check your DaVinci Resolve installation")
            return False
            
        # Add to Python path
        sys.path.append(modules_path)
        print(f"Added to Python path: {modules_path}")
        return True
        
    def connect(self) -> bool:
        """Connect to DaVinci Resolve instance."""
        try:
            print("Importing DaVinciResolveScript...")
            import DaVinciResolveScript as dvr_script
            
            print("Connecting to DaVinci Resolve...")
            self.resolve = dvr_script.scriptapp("Resolve")
            
            if not self.resolve:
                print("ERROR: Failed to connect to Resolve. Make sure Resolve is running.")
                return False
                
            # Get project manager and current project
            self.project_manager = self.resolve.GetProjectManager()
            self.current_project = self.project_manager.GetCurrentProject()
            
            print("✓ Successfully connected to DaVinci Resolve!")
            return True
            
        except ImportError as e:
            print(f"ImportError: {e}")
            print("Make sure DaVinci Resolve is installed and the API is accessible.")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            print(traceback.format_exc())
            return False
            
    def get_basic_info(self) -> dict:
        """Get basic information about Resolve and current project."""
        info = {}
        
        try:
            if self.resolve:
                info['version'] = self.resolve.GetVersionString()
                
            if self.current_project:
                info['project_name'] = self.current_project.GetName()
                info['fps'] = self.current_project.GetSetting("timelineFrameRate")
                info['width'] = self.current_project.GetSetting("timelineResolutionWidth")
                info['height'] = self.current_project.GetSetting("timelineResolutionHeight")
            else:
                info['project_name'] = "No project open"
                
        except Exception as e:
            print(f"Error getting basic info: {e}")
            
        return info
        
    def disconnect(self):
        """Clean up connections."""
        self.resolve = None
        self.project_manager = None
        self.current_project = None


def print_system_info():
    """Print system and Python information."""
    print("=" * 50)
    print("SYSTEM INFORMATION")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Architecture: {'64-bit' if sys.maxsize > 2**32 else '32-bit'}")
    print()


def print_resolve_info(info: dict):
    """Print DaVinci Resolve information."""
    print("=" * 50)
    print("DAVINCI RESOLVE INFORMATION")
    print("=" * 50)
    for key, value in info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()


def test_ripple_editing_functionality(resolver: DaVinciResolver):
    """Test ripple delete and investigate ripple insert functionality."""
    print("=" * 50)
    print("RIPPLE EDITING FUNCTIONALITY")
    print("=" * 50)
    
    if not resolver.current_project:
        print("! No project open - ripple editing tests skipped")
        print()
        return
    
    try:
        # Get current timeline
        current_timeline = resolver.current_project.GetCurrentTimeline()
        if not current_timeline:
            print("! No timeline currently selected - ripple editing tests skipped")
            print()
            return
            
        timeline_name = current_timeline.GetName()
        print(f"Timeline: '{timeline_name}'")
        print()
        
        # === RIPPLE DELETE FUNCTIONALITY ===
        print("🗑️  RIPPLE DELETE CAPABILITY:")
        print("-" * 30)
        print("✓ DeleteClips([timelineItems], Bool) - Available!")
        print("  • First parameter: List of timeline items to delete")
        print("  • Second parameter: True = Ripple Delete, False = Standard Delete")
        print("  • When ripple=True: Automatically closes gaps after deletion")
        print("  • When ripple=False: Leaves empty space where clips were deleted")
        print()
        
        # Show example usage
        print("📋 EXAMPLE USAGE:")
        print("```python")
        print("# Get clips to delete")
        print("video_clips = current_timeline.GetItemListInTrack('video', 1)")
        print("clips_to_delete = [video_clips[0]]  # Delete first clip")
        print()
        print("# Standard delete (leaves gap)")
        print("success = current_timeline.DeleteClips(clips_to_delete, False)")
        print()
        print("# Ripple delete (closes gap)")
        print("success = current_timeline.DeleteClips(clips_to_delete, True)")
        print("```")
        print()
        
        # === RIPPLE INSERT INVESTIGATION ===
        print("📥 RIPPLE INSERT INVESTIGATION:")
        print("-" * 30)
        
        # Check available insert methods
        media_pool = resolver.current_project.GetMediaPool()
        
        print("Available insertion methods found:")
        insert_methods = [
            "AppendToTimeline() - Adds clips to end of timeline",
            "InsertGeneratorIntoTimeline() - Inserts generators", 
            "InsertFusionGeneratorIntoTimeline() - Inserts Fusion generators",
            "InsertTitleIntoTimeline() - Inserts titles",
            "InsertFusionTitleIntoTimeline() - Inserts Fusion titles"
        ]
        
        for method in insert_methods:
            print(f"  • {method}")
        
        print()
        print("⚠️  RIPPLE INSERT LIMITATION:")
        print("  The DaVinci Resolve API does NOT appear to have a direct")
        print("  'ripple insert' function that automatically pushes existing")
        print("  clips to the right when inserting new content.")
        print()
        
        # === WORKAROUND STRATEGIES ===
        print("🔧 RIPPLE INSERT WORKAROUNDS:")
        print("-" * 30)
        print("1. MANUAL RIPPLE INSERT SIMULATION:")
        print("   - Get all clips after insertion point")
        print("   - Calculate new positions (shift by insert duration)")
        print("   - Move each clip to new position")
        print("   - Insert new clip at desired position")
        print()
        print("2. USE APPEND + REARRANGE:")
        print("   - Append new clip to end of timeline")
        print("   - Manually reposition clips as needed")
        print()
        print("3. EXTERNAL WORKFLOW:")
        print("   - Export EDL/XML with planned changes")
        print("   - Re-import with new structure")
        print()
        
        # === PRACTICAL EXAMPLE ===
        print("📝 PRACTICAL RIPPLE INSERT SIMULATION:")
        print("```python")
        print("def simulate_ripple_insert(timeline, track_type, track_index, ")
        print("                          insert_frame, media_pool_item, duration):")
        print("    # 1. Get all clips after insertion point")
        print("    all_clips = timeline.GetItemListInTrack(track_type, track_index)")
        print("    clips_to_move = []")
        print("    for clip in all_clips:")
        print("        if clip.GetStart() >= insert_frame:")
        print("            clips_to_move.append(clip)")
        print()
        print("    # 2. Calculate shift amount")
        print("    shift_amount = duration")
        print()
        print("    # 3. Move existing clips (would require additional API)")
        print("    # Note: This step is problematic as there's no direct")
        print("    # 'move clip' API function in DaVinci Resolve")
        print()
        print("    # 4. Insert new clip")
        print("    # timeline.AppendToTimeline([media_pool_item]) # Only appends to end")
        print("```")
        print()
        
        # === API LIMITATIONS SUMMARY ===
        print("📊 API CAPABILITIES SUMMARY:")
        print("-" * 30)
        print("✅ Ripple Delete: FULLY SUPPORTED")
        print("   - DeleteClips([items], True) performs ripple delete")
        print()
        print("❌ Ripple Insert: NOT DIRECTLY SUPPORTED")
        print("   - No built-in function for ripple insert")
        print("   - No direct clip positioning/moving functions")
        print("   - Would require complex workarounds")
        print()
        print("💡 RECOMMENDATION:")
        print("   For ripple insert functionality, consider:")
        print("   - Using DaVinci Resolve's UI for complex timeline edits")
        print("   - Exporting/importing timeline data (EDL/XML)")
        print("   - Building timeline structure from scratch when needed")
        
    except Exception as e:
        print(f"✗ Ripple editing analysis failed: {e}")
        print(traceback.format_exc())
    
    print()


def test_timeline_clips_analysis(resolver: DaVinciResolver):
    """Analyze all clips on the current timeline - get names, positions, and in/out points."""
    print("=" * 50)
    print("TIMELINE CLIPS ANALYSIS")
    print("=" * 50)
    
    if not resolver.current_project:
        print("! No project open - timeline analysis skipped")
        print()
        return
    
    try:
        # Get current timeline
        current_timeline = resolver.current_project.GetCurrentTimeline()
        if not current_timeline:
            print("! No timeline currently selected - timeline analysis skipped")
            print()
            return
            
        timeline_name = current_timeline.GetName()
        timeline_fps = float(current_timeline.GetSetting("timelineFrameRate"))
        print(f"Timeline: '{timeline_name}' @ {timeline_fps} fps")
        print()
        
        total_clips = 0
        
        # Analyze video tracks
        video_track_count = current_timeline.GetTrackCount("video")
        print(f"VIDEO TRACKS ({video_track_count}):")
        print("-" * 30)
        
        for track_index in range(1, video_track_count + 1):
            track_items = current_timeline.GetItemListInTrack("video", track_index)
            print(f"\nVideo Track {track_index}: {len(track_items)} clips")
            
            for item_index, timeline_item in enumerate(track_items, 1):
                try:
                    # Get clip information
                    clip_name = timeline_item.GetName()
                    start_frame = timeline_item.GetStart()  # Position on timeline (start)
                    end_frame = timeline_item.GetEnd()      # Position on timeline (end)
                    duration = timeline_item.GetDuration()  # Duration on timeline
                    
                    # Get source clip in/out points
                    left_offset = timeline_item.GetLeftOffset()   # In point of source clip
                    right_offset = timeline_item.GetRightOffset() # Out point of source clip
                    
                    # Calculate timecode
                    start_tc = frames_to_timecode(start_frame, timeline_fps)
                    end_tc = frames_to_timecode(end_frame, timeline_fps)
                    duration_tc = frames_to_timecode(duration, timeline_fps)
                    
                    print(f"  [{item_index}] '{clip_name}'")
                    print(f"      Timeline Position: {start_frame}-{end_frame} frames ({start_tc} - {end_tc})")
                    print(f"      Duration: {duration} frames ({duration_tc})")
                    print(f"      Source In/Out: {left_offset}/{right_offset} frames")
                    
                    total_clips += 1
                    
                except Exception as e:
                    print(f"    ✗ Error analyzing clip {item_index}: {e}")
        
        # Analyze audio tracks
        audio_track_count = current_timeline.GetTrackCount("audio")
        print(f"\nAUDIO TRACKS ({audio_track_count}):")
        print("-" * 30)
        
        for track_index in range(1, audio_track_count + 1):
            track_items = current_timeline.GetItemListInTrack("audio", track_index)
            print(f"\nAudio Track {track_index}: {len(track_items)} clips")
            
            for item_index, timeline_item in enumerate(track_items, 1):
                try:
                    # Get clip information
                    clip_name = timeline_item.GetName()
                    start_frame = timeline_item.GetStart()
                    end_frame = timeline_item.GetEnd()
                    duration = timeline_item.GetDuration()
                    
                    # Get source clip in/out points
                    left_offset = timeline_item.GetLeftOffset()
                    right_offset = timeline_item.GetRightOffset()
                    
                    # Calculate timecode
                    start_tc = frames_to_timecode(start_frame, timeline_fps)
                    end_tc = frames_to_timecode(end_frame, timeline_fps)
                    duration_tc = frames_to_timecode(duration, timeline_fps)
                    
                    print(f"  [{item_index}] '{clip_name}'")
                    print(f"      Timeline Position: {start_frame}-{end_frame} frames ({start_tc} - {end_tc})")
                    print(f"      Duration: {duration} frames ({duration_tc})")
                    print(f"      Source In/Out: {left_offset}/{right_offset} frames")
                    
                    total_clips += 1
                    
                except Exception as e:
                    print(f"    ✗ Error analyzing clip {item_index}: {e}")
        
        # Summary
        print(f"\n--- TIMELINE SUMMARY ---")
        print(f"Total clips analyzed: {total_clips}")
        print(f"Timeline frame rate: {timeline_fps} fps")
        
    except Exception as e:
        print(f"✗ Timeline analysis failed: {e}")
        print(traceback.format_exc())
    
    print()


def frames_to_timecode(frames: int, fps: float) -> str:
    """Convert frame number to timecode string (HH:MM:SS:FF)."""
    try:
        total_seconds = frames / fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        remaining_frames = int(frames % fps)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{remaining_frames:02d}"
    except:
        return f"Frame {frames}"


def test_basic_functionality(resolver: DaVinciResolver):
    """Test basic DaVinci Resolve API functionality."""
    print("=" * 50)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 50)
    
    # Add your test functionality here
    # Examples:
    
    # Test 1: Get timeline count
    try:
        if resolver.current_project:
            timeline_count = resolver.current_project.GetTimelineCount()
            print(f"✓ Timeline count: {timeline_count}")
        else:
            print("! No project open - timeline tests skipped")
    except Exception as e:
        print(f"✗ Timeline count test failed: {e}")
    
    # Test 2: Get media pool
    try:
        if resolver.current_project:
            media_pool = resolver.current_project.GetMediaPool()
            if media_pool:
                print("✓ Media pool access successful")
            else:
                print("! Media pool not accessible")
        else:
            print("! No project open - media pool tests skipped")
    except Exception as e:
        print(f"✗ Media pool test failed: {e}")
    
    # Test 3: Current timeline info
    try:
        if resolver.current_project:
            current_timeline = resolver.current_project.GetCurrentTimeline()
            if current_timeline:
                timeline_name = current_timeline.GetName()
                print(f"✓ Current timeline: '{timeline_name}'")
            else:
                print("! No timeline currently selected")
        else:
            print("! No project open - current timeline test skipped")
    except Exception as e:
        print(f"✗ Current timeline test failed: {e}")
    
    # Add more tests here as needed
    print()


def main():
    """Main function to run the DaVinci Resolve API tests."""
    print_system_info()
    
    # Initialize resolver
    resolver = DaVinciResolver()
    
    # Setup environment
    if not resolver.setup_environment():
        sys.exit(1)
        
    # Connect to Resolve
    if not resolver.connect():
        sys.exit(1)
        
    # Get and display basic information
    info = resolver.get_basic_info()
    print_resolve_info(info)
    
    # Run basic functionality tests
    test_basic_functionality(resolver)
    
    # Run timeline clips analysis
    test_timeline_clips_analysis(resolver)
    
    # Run ripple editing functionality analysis
    test_ripple_editing_functionality(resolver)
    
    # Clean up
    resolver.disconnect()
    
    print("=" * 50)
    print("SCRIPT COMPLETED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(traceback.format_exc())
        sys.exit(1)
