// Text-to-Speech using Web Speech API (browser native, free)
export class SpeechService {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.recognition = null;
    this.isListening = false;
    
    // Initialize speech recognition if supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';
    }
  }

  // Text-to-Speech
  speak(text, options = {}) {
    return new Promise((resolve, reject) => {
      // Cancel any ongoing speech
      this.synthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Configure voice
      const voices = this.synthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith('en') && voice.name.includes('Female')
      ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      utterance.rate = options.rate || 0.95;
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 1.0;
      
      utterance.onend = () => resolve();
      utterance.onerror = (error) => reject(error);
      
      if (options.onStart) {
        utterance.onstart = options.onStart;
      }
      
      this.synthesis.speak(utterance);
    });
  }

  stopSpeaking() {
    this.synthesis.cancel();
  }

  isSpeaking() {
    return this.synthesis.speaking;
  }

  // Speech-to-Text
  startListening(onResult, onEnd, onError) {
    if (!this.recognition) {
      onError?.(new Error('Speech recognition not supported in this browser'));
      return;
    }

    let finalTranscript = '';
    
    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      
      onResult?.({
        interim: interimTranscript,
        final: finalTranscript.trim()
      });
    };

    this.recognition.onend = () => {
      this.isListening = false;
      onEnd?.(finalTranscript.trim());
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      onError?.(event.error);
    };

    this.recognition.start();
    this.isListening = true;
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  isRecognitionSupported() {
    return this.recognition !== null;
  }

  // Get available voices
  getVoices() {
    return new Promise((resolve) => {
      let voices = this.synthesis.getVoices();
      
      if (voices.length > 0) {
        resolve(voices);
      } else {
        this.synthesis.onvoiceschanged = () => {
          voices = this.synthesis.getVoices();
          resolve(voices);
        };
      }
    });
  }
}

// Create singleton instance
export const speechService = new SpeechService();
