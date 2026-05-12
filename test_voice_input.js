// Test script for voice input functionality
// This would typically be run in the browser console or as part of E2E tests

function testVoiceInput() {
  console.log('Testing voice input functionality...');

  // Check if speech recognition is available
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.log('❌ Speech recognition not supported in this browser');
    return false;
  }

  console.log('✅ Speech recognition is supported');

  // Create a test recognition instance
  const recognition = new SpeechRecognition();
  console.log('✅ Speech recognition object created');

  // Check if we can start recognition
  try {
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;

    console.log('✅ Recognition settings configured');

    // Set up event handlers
    recognition.onresult = (event) => {
      console.log('✅ Successfully received speech result');
      console.log('Transcript:', event.results[0][0].transcript);
    };

    recognition.onerror = (event) => {
      console.log('❌ Speech recognition error:', event.error);
    };

    recognition.onend = () => {
      console.log('✅ Speech recognition stopped');
    };

    console.log('✅ All event handlers set up');

    return true;
  } catch (error) {
    console.log('❌ Error setting up speech recognition:', error);
    return false;
  }
}

// Run the test
const testResult = testVoiceInput();
console.log('Voice input test result:', testResult ? 'PASS' : 'FAIL');

// Additional test: check if our utility works
if (window.voiceRecognition) {
  console.log('✅ Voice recognition utility is available');
  console.log('Browser supported:', window.voiceRecognition.isBrowserSupported());
} else {
  console.log('⚠️ Voice recognition utility not found - may need to load the component first');
}