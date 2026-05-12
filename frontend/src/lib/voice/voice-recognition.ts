/**
 * Voice Recognition and Transcription Utilities
 *
 * Provides speech-to-text functionality using browser APIs and potentially OpenAI's Whisper API
 */

interface VoiceRecognitionOptions {
  lang?: string;
  interimResults?: boolean;
  continuous?: boolean;
  useWhisperAPI?: boolean; // Flag to use OpenAI Whisper API instead of browser API
}

class VoiceRecognition {
  private recognition: any | null = null;
  private isSupported: boolean;
  private apiKey: string | null = null;

  constructor(options: VoiceRecognitionOptions = {}) {
    this.isSupported = this.checkSupport();

    if (this.isSupported) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition ||
                               (window as any).SpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();

        // Set options
        this.recognition.continuous = options.continuous ?? false;
        this.recognition.interimResults = options.interimResults ?? true;
        this.recognition.lang = options.lang ?? 'en-US';
      }
    }
  }

  /**
   * Check if the browser supports speech recognition
   */
  private checkSupport(): boolean {
    return typeof window !== 'undefined' &&
           ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
  }

  /**
   * Check if browser supports the required APIs
   */
  isBrowserSupported(): boolean {
    return this.isSupported;
  }

  /**
   * Start voice recognition
   */
  start(
    onResult: (transcript: string) => void,
    onError?: (error: any) => void,
    onEnd?: () => void
  ): void {
    if (!this.isSupported) {
      throw new Error('Speech recognition is not supported in this browser');
    }

    if (this.recognition) {
      this.recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        onResult(transcript);
      };

      this.recognition.onerror = (event: any) => {
        if (onError) {
          onError(event.error);
        }
      };

      this.recognition.onend = () => {
        if (onEnd) {
          onEnd();
        }
      };

      this.recognition.start();
    }
  }

  /**
   * Stop voice recognition
   */
  stop(): void {
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  /**
   * Set OpenAI API key for Whisper API usage
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Transcribe audio using OpenAI's Whisper API
   * Note: This requires audio data in a specific format (e.g., WAV, MP3, etc.)
   */
  async transcribeWithWhisper(audioBlob: Blob): Promise<string> {
    if (!this.apiKey) {
      throw new Error('OpenAI API key is required for Whisper API');
    }

    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');
    formData.append('model', 'whisper-1');

    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Transcription failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.text;
  }
}

// Export singleton instance
const voiceRecognition = new VoiceRecognition();

export {
  VoiceRecognition,
  voiceRecognition,
  type VoiceRecognitionOptions
};