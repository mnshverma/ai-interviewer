const KILO_API_URL = "https://api.kilo.ai/api/gateway/chat/completions";

// Default model: Let Kilo auto-route to the best free model
const DEFAULT_MODEL = 'kilo-auto/free';

// Fallback models (official Kilo free apis)
const FREE_FALLBACK_MODELS = [
  'minimax/minimax-m2.5:free',
  'z-ai/glm-5:free',
  'corethink:free',
  'giga-potato',
  'arcee-ai/trinity-large-preview:free'
];

// Get API key from environment variable
const getApiKey = () => {
  const key = import.meta.env.VITE_KILO_API_KEY;
  if (!key || key.trim() === '') {
    // Falls back to anonymous mode supported by Kilo Gateway
    return null;
  }
  return key.trim();
};

// Helper: make an API call with automatic fallback on 402/429
const callWithFallback = async (apiKey, messages, options = {}) => {
  const { temperature = 0.7, max_tokens = 1000, model } = options;
  const preferredModel = model && model !== DEFAULT_MODEL ? model : DEFAULT_MODEL;
  
  const modelsToTry = [preferredModel, ...FREE_FALLBACK_MODELS];
  // Deduplicate
  const uniqueModels = [...new Set(modelsToTry)];

  let lastError = null;

  for (const currentModel of uniqueModels) {
    try {
      console.log(`[AI Gateway] Attempting call with model: ${currentModel}`);
      
      const headers = {
        'Content-Type': 'application/json'
      };

      if (apiKey) {
        headers['Authorization'] = `Bearer ${apiKey}`;
      }

      const response = await fetch(KILO_API_URL, {
        method: 'POST',
        headers: headers,
        mode: 'cors',
        body: JSON.stringify({
          model: currentModel,
          messages,
          temperature,
          max_tokens,
        }),
      });

      if (response.status === 402 || response.status === 429) {
        console.warn(`[AI Gateway] Model ${currentModel} rate limited/payment required (Status ${response.status}). Trying fallback...`);
        lastError = new Error(`Model ${currentModel}: HTTP ${response.status}`);
        continue;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const msg = errorData.error?.message || `Gateway returned ${response.status}`;
        throw new Error(msg);
      }

      const data = await response.json();
      if (!data.choices?.[0]?.message?.content) {
        throw new Error('Malformed response from AI gateway');
      }

      return data.choices[0].message.content;
    } catch (error) {
      console.error(`[AI Gateway] Error with ${currentModel}:`, error);
      lastError = error;
      
      // If it's a "Failed to fetch" (Network Error / CORS), don't bother retrying other models
      // as they all use the same endpoint.
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error('Network error or CORS block. Please check your internet connection or try a different browser.');
      }
      
      continue;
    }
  }

  throw lastError || new Error('All models failed to respond.');
};

export const analyzeResume = async (resumeText, model = DEFAULT_MODEL) => {
  try {
    const apiKey = getApiKey();
    const analysisText = await callWithFallback(apiKey, [
      {
        role: "system",
        content: `You are an expert technical recruiter. Analyze resumes and extract key info.`,
      },
      {
        role: "user",
        content: `Analyze this resume and extract candidate name, experience, skills, and roles.\n\nResume:\n${resumeText}\n\nProvide a structured summary.`,
      },
    ], { temperature: 0.7, max_tokens: 1000, model });

    return { success: true, analysis: analysisText };
  } catch (error) {
    console.error("Resume analysis error:", error);
    return { success: false, error: error.message };
  }
};

export const analyzeJobDescription = async (jobDescText, model = DEFAULT_MODEL) => {
  try {
    const apiKey = getApiKey();
    const analysisText = await callWithFallback(apiKey, [
      {
        role: 'system',
        content: `Analyze job descriptions to prepare assessment criteria.`
      },
      {
        role: 'user',
        content: `Job Description:\n${jobDescText}\n\nExtract key requirements and responsibilities.`
      }
    ], { temperature: 0.7, max_tokens: 1000, model });

    return { success: true, analysis: analysisText };
  } catch (error) {
    console.error('Job analysis error:', error);
    return { success: false, error: error.message };
  }
};

export const generateInterviewQuestions = async (resumeAnalysis, interviewType, model = DEFAULT_MODEL, difficulty = 'medium') => {
  try {
    const apiKey = getApiKey();
    const questionsText = await callWithFallback(apiKey, [
      {
        role: "system",
        content: `You are an experienced ${interviewType} interviewer. Generate level ${difficulty} questions.`,
      },
      {
        role: "user",
        content: `Based on this background, generate 8-10 numbered interview questions.\n\nBackground:\n${resumeAnalysis}`,
      },
    ], { temperature: 0.8, max_tokens: 1500, model });

    const questions = questionsText
      .split("\n")
      .filter((line) => /^\d+\./.test(line.trim()))
      .map((q) => q.replace(/^\d+\.\s*/, "").trim())
      .filter((q) => q.length > 0);

    return { success: true, questions };
  } catch (error) {
    console.error("Question generation error:", error);
    return { success: false, error: error.message, questions: [] };
  }
};

export const evaluateAnswer = async (question, answer, context, model = DEFAULT_MODEL) => {
  try {
    const apiKey = getApiKey();
    const feedback = await callWithFallback(apiKey, [
      { role: "system", content: "Evaluate interview answers constructively." },
      { role: "user", content: `Context: ${context}\nQuestion: ${question}\nAnswer: ${answer}\n\nProvide 2-3 sentences of feedback.` }
    ], { temperature: 0.7, max_tokens: 200, model });
    return { success: true, feedback };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const generateFinalReport = async (transcript, resumeAnalysis, model = DEFAULT_MODEL) => {
  try {
    const apiKey = getApiKey();
    const report = await callWithFallback(apiKey, [
      { role: "system", content: "Create an interview evaluation report." },
      { role: "user", content: `Resume: ${resumeAnalysis}\nTranscript: ${transcript}\n\nProvide a detailed report with RESULT: PASS/FAIL, scores, and hire recommendation.` }
    ], { temperature: 0.7, max_tokens: 2000, model });
    return { success: true, report };
  } catch (error) {
    return { success: false, error: error.message };
  }
};
