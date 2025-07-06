import os
import sys
import tempfile
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def get_executable_dir():
    """
    Returns the directory where the executable is located.
    For PyInstaller frozen apps, this is sys.executable's directory.
    For regular Python scripts, this is the directory of the current script.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_current_working_dir():
    """Returns the current working directory."""
    return os.getcwd()

def get_output_dir(create=True):
    """
    Determines the best directory for output files.
    1. Tries environment variable OUTPUT_DIR if set
    2. Tries a 'json_outputs' directory next to the executable
    3. Falls back to current working directory if needed
    
    Args:
        create (bool): Whether to create the directory if it doesn't exist
    
    Returns:
        str: Path to the output directory
    """
    # Check for environment variable first
    env_dir = os.environ.get('ONEPYFLOW_OUTPUT_DIR')
    if env_dir:
        logger.info(f"Using output directory from environment variable: {env_dir}")
        path = env_dir
    else:
        # Try executable directory
        exe_dir = get_executable_dir()
        path = os.path.join(exe_dir, 'json_outputs')
        logger.info(f"Using output directory next to executable: {path}")
    
    # Create directory if it doesn't exist
    if create and not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created output directory: {path}")
        except Exception as e:
            logger.error(f"Failed to create output directory {path}: {e}")
            # Fall back to current working directory
            path = os.path.join(get_current_working_dir(), 'json_outputs')
            try:
                os.makedirs(path, exist_ok=True)
                logger.info(f"Falling back to current directory: {path}")
            except Exception as e2:
                logger.error(f"Failed to create fallback directory: {e2}")
                # Last resort: use temp directory
                path = os.path.join(tempfile.gettempdir(), 'onepyflow_outputs')
                os.makedirs(path, exist_ok=True)
                logger.info(f"Using temp directory as last resort: {path}")
    
    # Test if we can write to this directory
    test_file = os.path.join(path, 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"Successfully verified write access to: {path}")
    except Exception as e:
        logger.error(f"Cannot write to output directory {path}: {e}")
        # Fall back to temp directory
        path = os.path.join(tempfile.gettempdir(), 'onepyflow_outputs')
        os.makedirs(path, exist_ok=True)
        logger.info(f"Falling back to temp directory: {path}")
        
    return path

def get_temp_dir():
    """
    Returns a suitable directory for temporary files.
    Creates a 'temp' subdirectory in the executable directory if possible,
    otherwise falls back to system temp directory.
    """
    # Try to use a subdirectory of the executable location
    exe_dir = get_executable_dir()
    temp_dir = os.path.join(exe_dir, 'temp')
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        # Test write access
        test_file = os.path.join(temp_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"Using temp directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        # If any issues, use system temp directory
        system_temp = tempfile.gettempdir()
        temp_dir = os.path.join(system_temp, 'onepyflow_temp')
        os.makedirs(temp_dir, exist_ok=True)
        logger.info(f"Using system temp directory: {temp_dir}")
        return temp_dir