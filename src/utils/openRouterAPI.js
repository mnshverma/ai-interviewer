const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";

// Get API key from environment variable
const getApiKey = () => {
  const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
  if (!apiKey) {
    throw new Error('OpenRouter API key not configured. Please set VITE_OPENROUTER_API_KEY in environment variables.');
  }
  return apiKey;
};

export const analyzeResume = async (resumeText, model = 'meta-llama/llama-3.3-70b-instruct:free') => {
  try {
    const apiKey = getApiKey();

    const response = await fetch(OPENROUTER_API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": window.location.origin,
        "X-Title": "AI Interviewer",
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: "system",
            content: `You are an expert technical recruiter and interviewer. Analyze resumes and extract key information to generate relevant interview questions.`,
          },
          {
            role: "user",
            content: `Analyze this resume and extract:
1. Candidate's name
2. Years of experience
3. Key skills (list top 5-7)
4. Previous roles/companies
5. Educational background
6. Notable projects or achievements

Resume:
${resumeText}

Provide the analysis in a structured JSON format.`,
          },
        ],
        temperature: 0.7,
        max_tokens: 1000,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    const analysisText = data.choices[0].message.content;

    return {
      success: true,
      analysis: analysisText,
      rawText: resumeText,
    };
  } catch (error) {
    console.error("Resume analysis error:", error);
    return {
      success: false,
      error: error.message,
    };
  }
};

export const analyzeJobDescription = async (jobDescText, model = 'meta-llama/llama-3.3-70b-instruct:free') => {
  try {
    const apiKey = getApiKey();
    const response = await fetch(OPENROUTER_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.origin,
        'X-Title': 'AI Interviewer'
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: 'system',
            content: `You are an expert recruiter analyzing job descriptions to prepare interview questions.`
          },
          {
            role: 'user',
            content: `Analyze this job description and extract:
1. Role/Position title
2. Required years of experience
3. Key technical skills required
4. Soft skills needed
5. Responsibilities
6. Company culture indicators

Job Description:
${jobDescText}

Provide the analysis in a structured format highlighting what to assess in interviews.`
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      })
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    const analysisText = data.choices[0].message.content;
    
    return {
      success: true,
      analysis: analysisText,
      rawText: jobDescText
    };
  } catch (error) {
    console.error('Job description analysis error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export const generateInterviewQuestions = async (
  resumeAnalysis,
  interviewType,
  model = 'meta-llama/llama-3.3-70b-instruct:free'
) => {
  try {
    const apiKey = getApiKey();

    const response = await fetch(OPENROUTER_API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": window.location.origin,
        "X-Title": "AI Interviewer",
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: "system",
            content: `You are an experienced ${interviewType} interviewer. Generate relevant, thoughtful interview questions based on the candidate's background.`,
          },
          {
            role: "user",
            content: `Based on this resume analysis, generate 8-10 ${interviewType} interview questions that are:
1. Relevant to the candidate's experience
2. Progressive in difficulty
3. Mix of technical and behavioral (if technical interview)
4. Designed to assess real-world problem-solving

Resume Analysis:
${resumeAnalysis}

Format each question on a new line, numbered 1-10.`,
          },
        ],
        temperature: 0.8,
        max_tokens: 1500,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    const questionsText = data.choices[0].message.content;

    // Parse questions into array
    const questions = questionsText
      .split("\n")
      .filter((line) => /^\d+\./.test(line.trim()))
      .map((q) => q.replace(/^\d+\.\s*/, "").trim());

    return {
      success: true,
      questions,
    };
  } catch (error) {
    console.error("Question generation error:", error);
    return {
      success: false,
      error: error.message,
      questions: [],
    };
  }
};

export const evaluateAnswer = async (question, answer, context, model = 'meta-llama/llama-3.3-70b-instruct:free') => {
  try {
    const apiKey = getApiKey();
    const response = await fetch(OPENROUTER_API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": window.location.origin,
        "X-Title": "AI Interviewer",
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: "system",
            content:
              "You are an interview evaluator. Provide brief, constructive feedback on answers.",
          },
          {
            role: "user",
            content: `Context: ${context}
Question: ${question}
Answer: ${answer}

Provide a brief evaluation (2-3 sentences) on:
1. Relevance and completeness
2. Technical accuracy (if applicable)
3. Communication clarity`,
          },
        ],
        temperature: 0.7,
        max_tokens: 200,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      feedback: data.choices[0].message.content,
    };
  } catch (error) {
    console.error("Answer evaluation error:", error);
    return {
      success: false,
      error: error.message,
    };
  }
};

export const generateFinalReport = async (
  transcript,
  resumeAnalysis,
  model = 'meta-llama/llama-3.3-70b-instruct:free'
) => {
  try {
    const apiKey = getApiKey();
    const response = await fetch(OPENROUTER_API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": window.location.origin,
        "X-Title": "AI Interviewer",
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: "system",
            content:
              "You are an expert interviewer creating a comprehensive interview evaluation report.",
          },
          {
            role: "user",
            content: `Generate a detailed interview evaluation report based on:

Resume Analysis:
${resumeAnalysis}

Interview Transcript:
${transcript}

IMPORTANT: Start with a clear overall result:
**RESULT: PASS** or **RESULT: FAIL**

Then include:
1. Overall Performance Score (1-10)
2. Key Strengths (3-5 points)
3. Areas for Improvement (3-5 points)
4. Technical Competency Assessment
5. Communication Skills Rating
6. Hiring Recommendation (Strong Hire / Hire / Maybe / No Hire)
7. Detailed Notes

Format as a clear, structured report.`,
          },
        ],
        temperature: 0.7,
        max_tokens: 2000,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      report: data.choices[0].message.content,
    };
  } catch (error) {
    console.error("Report generation error:", error);
    return {
      success: false,
      error: error.message,
    };
  }
};
