# Threading Improvements Plan for AutoTyper

## Issues Identified:

1. **main.py**:
   - `stop_event` created but never used
   - No thread cleanup (join threads)
   - SettingsWindow blocks main thread
   - No thread pool for managing multiple typing tasks

2. **core/shortcut_listener.py**:
   - No daemon thread setup
   - `running` flag not properly used

3. **core/voice_engine.py**:
   - Recording runs synchronously (blocking)

4. **General**:
   - No proper shutdown handling
   - Thread safety gaps

## Improvements to Implement:

### 1. main.py
- [ ] Use `stop_event` for proper shutdown signaling
- [ ] Add thread pool using `concurrent.futures.ThreadPoolExecutor`
- [ ] Add thread tracking and proper cleanup (join threads on exit)
- [ ] Run SettingsWindow in separate thread to avoid blocking

### 2. core/shortcut_listener.py
- [ ] Run listener in a proper daemon thread
- [ ] Add thread-safe running flag using Lock

### 3. core/voice_engine.py
- [ ] Already uses queue.Queue which is thread-safe
- [ ] Keep as is since it's called from a thread

### 4. core/typing_engine.py
- [ ] Already has proper thread-safe implementation with Lock
- [ ] Add daemon thread flag support
