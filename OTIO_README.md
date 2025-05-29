# DaVinci Resolve OTIO Import/Export Tool

A comprehensive Python script for importing and exporting OpenTimelineIO (OTIO) files with DaVinci Resolve.

## Features

- **Export timelines** from DaVinci Resolve to OTIO format
- **Import OTIO files** into DaVinci Resolve as new timelines
- **List timelines** in the current project
- Cross-platform support (Windows, macOS, Linux)
- Robust error handling and logging
- Command-line interface for automation

## Prerequisites

1. **DaVinci Resolve** must be installed and running
2. **Python 3.6+** (64-bit) - DaVinci Resolve API requires 64-bit Python
3. A project must be open in DaVinci Resolve

## Installation & Setup

1. Ensure DaVinci Resolve is installed in the default location
2. No additional Python packages required (uses only built-in modules)
3. Make sure your Python installation is 64-bit

## Usage

### Command-Line Interface

```bash
# List all timelines in the current project
python importexport.py list

# Export a timeline to OTIO format
python importexport.py export "Timeline Name" output.otio

# Import an OTIO file (timeline name will be the filename)
python importexport.py import timeline.otio

# Import an OTIO file with a custom timeline name
python importexport.py import timeline.otio "My Custom Timeline"
```

### Examples

#### 1. List Available Timelines
```bash
python importexport.py list
```
Output:
```
Setting up DaVinci Resolve API environment...
API modules path: C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules
Connecting to DaVinci Resolve...
✓ Connected to DaVinci Resolve 19.1.0
✓ Current project: My Project

Found 3 timeline(s) in project:
  1. Main Timeline (frames 1001-2000, duration: 1000)
  2. Rough Cut (frames 1001-1500, duration: 500)
  3. Final Cut (frames 1001-2500, duration: 1500)
```

#### 2. Export Timeline to OTIO
```bash
python importexport.py export "Main Timeline" exports/main_timeline.otio
```

#### 3. Import OTIO File
```bash
python importexport.py import exports/main_timeline.otio "Imported Timeline"
```

## Programmatic Usage

You can also use the classes directly in your Python scripts:

```python
from importexport import ResolveConnection, OTIOExporter, OTIOImporter

# Establish connection
connection = ResolveConnection()
connection.connect()

# Export a timeline
exporter = OTIOExporter(connection)
exporter.export_timeline("My Timeline", "output.otio")

# Import an OTIO file
importer = OTIOImporter(connection)
importer.import_otio("timeline.otio", "New Timeline Name")
```

## Advanced Features

### Import Options

The script automatically configures import options for best compatibility:

- **Source Clips**: Automatically imports source clips when available
- **Source Clips Path**: Looks for media in the same directory as the OTIO file
- **Timeline Naming**: Uses filename if no custom name provided
- **Current Timeline**: Automatically sets imported timeline as current

### Export Features

- **Automatic Extension**: Adds `.otio` extension if not provided
- **Directory Creation**: Creates output directories automatically
- **Timeline Validation**: Validates timeline exists before export
- **Current Timeline Setting**: Sets timeline as current before export

## Error Handling

The script includes comprehensive error handling for common issues:

### Connection Issues
```
❌ Error: Failed to connect to Resolve. Make sure Resolve is running.
```
**Solution**: Start DaVinci Resolve and open a project

### No Project Open
```
❌ Error: No project is currently open. Please open a project in DaVinci Resolve.
```
**Solution**: Open or create a project in DaVinci Resolve

### Timeline Not Found
```
❌ Error: Timeline 'NonExistent' not found. Available timelines: Timeline 1, Timeline 2
```
**Solution**: Use `list` command to see available timelines

### File Not Found
```
❌ Error: OTIO file not found: /path/to/missing.otio
```
**Solution**: Check the file path and ensure the OTIO file exists

## Debugging

Add `--debug` flag to see detailed error information:

```bash
python importexport.py export "Timeline" output.otio --debug
```

## File Structure

```
.
├── importexport.py       # Main script
├── OTIO_README.md        # This documentation
└── examples/
    ├── basic_usage.py    # Basic usage examples
    └── batch_export.py   # Batch export example
```

## Technical Notes

### OTIO Format Support

- **Export**: Uses `resolve.EXPORT_OTIO` constant
- **Import**: Leverages `MediaPool.ImportTimelineFromFile()` with OTIO support
- **Compatibility**: Works with standard OTIO files from other applications

### Platform Paths

The script automatically detects your platform and uses appropriate paths:

- **Windows**: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting`
- **macOS**: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting`
- **Linux**: `/opt/resolve/Developer/Scripting`

### Performance Considerations

- **Large Timelines**: Export time depends on timeline complexity
- **Source Media**: Import performance depends on media availability
- **Network Storage**: Use local paths for better performance

## Troubleshooting

### Common Issues

1. **"ImportError: No module named 'DaVinciResolveScript'"**
   - Ensure DaVinci Resolve is installed
   - Check that you're using 64-bit Python
   - Verify API modules path exists

2. **"Failed to connect to Resolve"**
   - Start DaVinci Resolve
   - Open a project
   - Check that scripting is enabled in Resolve preferences

3. **Export fails silently**
   - Check disk space
   - Verify write permissions
   - Ensure timeline has content

4. **Import creates empty timeline**
   - Check source media paths
   - Verify OTIO file integrity
   - Use absolute paths for media

### Getting Help

1. Use the `--debug` flag for detailed error information
2. Check DaVinci Resolve's Console window for additional logs
3. Verify your OTIO file with other OTIO-compatible applications

## Limitations

- Requires DaVinci Resolve to be running
- Limited to OTIO format (no other timeline formats)
- Source media paths may need adjustment after import
- Some DaVinci Resolve-specific effects may not transfer

## Future Enhancements

- Batch export/import functionality
- Media relinking assistance
- Progress bars for long operations
- Configuration file support
- Integration with other NLE applications 