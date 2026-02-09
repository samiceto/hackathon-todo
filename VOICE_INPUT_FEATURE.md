# Voice Input Feature for ChatBot

## Overview
This feature adds voice input capabilities to the ChatBot interface, allowing users to speak their messages instead of typing them. The implementation uses the Web Speech API for real-time speech-to-text conversion in the browser.

## Features
- Microphone button for voice input
- Real-time speech-to-text transcription
- Visual feedback during recording (pulsing red button)
- Browser compatibility detection
- Fallback to text input

## Implementation Details

### Frontend Components
- `MessageInput.tsx`: Updated with voice recording functionality
- `voice-recognition.ts`: Utility class for handling speech recognition
- Visual indicators and UI enhancements

### Technologies Used
- Web Speech API (SpeechRecognition interface)
- React hooks for state management
- Tailwind CSS for styling

## Browser Compatibility
- Chrome: Supported
- Edge: Supported
- Safari: Limited support
- Firefox: Not supported (API not available)

## Usage
1. Click the microphone icon next to the text input
2. Speak your message when the button turns red and pulses
3. The spoken words will appear as text in the input field
4. Click the microphone again to stop recording
5. Send the message as usual

## Configuration
The voice recognition can be configured with the following options:
- Language (default: 'en-US')
- Interim results (default: true)
- Continuous recognition (default: false)

## Future Enhancements
- Integration with OpenAI's Whisper API for improved accuracy
- Audio file upload and transcription
- Voice commands for specific actions
- Multi-language support