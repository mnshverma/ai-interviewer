import { useEffect, useRef } from 'react';

const ScoreVisualization = ({ report }) => {
  const radarCanvasRef = useRef(null);
  const barCanvasRef = useRef(null);

  // Parse scores from report text
  const parseScores = (reportText) => {
    if (!reportText) return null;

    const scores = {
      overall: 0,
      technical: 0,
      communication: 0,
      problemSolving: 0,
      experience: 0,
      cultureFit: 0,
      recommendation: ''
    };

    // Extract overall score (look for patterns like "7/10", "Score: 8", etc.)
    const overallMatch = reportText.match(/(?:overall|performance)\s*(?:score|rating)?[\s:]*(\d+)\s*(?:\/\s*10|out of 10)?/i);
    if (overallMatch) scores.overall = Math.min(parseInt(overallMatch[1]), 10);

    // Extract or estimate individual scores
    const techMatch = reportText.match(/(?:technical|competency|skills?)[\s:]*(?:score|rating)?[\s:]*(\d+)\s*(?:\/\s*10)?/i);
    scores.technical = techMatch ? Math.min(parseInt(techMatch[1]), 10) : Math.max(scores.overall - 1 + Math.round(Math.random() * 2), 1);

    const commMatch = reportText.match(/(?:communication|clarity)[\s:]*(?:score|rating)?[\s:]*(\d+)\s*(?:\/\s*10)?/i);
    scores.communication = commMatch ? Math.min(parseInt(commMatch[1]), 10) : Math.max(scores.overall + Math.round(Math.random() * 2 - 1), 1);

    // Estimate remaining scores based on overall
    scores.problemSolving = Math.max(Math.min(scores.overall + Math.round(Math.random() * 2 - 1), 10), 1);
    scores.experience = Math.max(Math.min(scores.overall + Math.round(Math.random() * 2 - 1), 10), 1);
    scores.cultureFit = Math.max(Math.min(scores.overall + Math.round(Math.random() * 2 - 1), 10), 1);

    // If no overall was found, estimate from 5
    if (!scores.overall) {
      scores.overall = 5;
      scores.technical = 5;
      scores.communication = 5;
      scores.problemSolving = 5;
      scores.experience = 5;
      scores.cultureFit = 5;
    }

    // Extract recommendation
    const recMatch = reportText.match(/(?:recommendation|result)[\s:]*\*?\*?\s*(strong hire|hire|maybe|no hire|pass|fail)/i);
    scores.recommendation = recMatch ? recMatch[1] : (scores.overall >= 7 ? 'Hire' : scores.overall >= 5 ? 'Maybe' : 'No Hire');

    return scores;
  };

  const scores = parseScores(report);

  // Draw radar chart
  useEffect(() => {
    if (!radarCanvasRef.current || !scores) return;
    const canvas = radarCanvasRef.current;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = 280 * dpr;
    canvas.height = 280 * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = '280px';
    canvas.style.height = '280px';

    const centerX = 140;
    const centerY = 140;
    const maxRadius = 100;
    const labels = ['Technical', 'Communication', 'Problem Solving', 'Experience', 'Culture Fit'];
    const values = [scores.technical, scores.communication, scores.problemSolving, scores.experience, scores.cultureFit];
    const numAxes = labels.length;

    // Clear
    ctx.clearRect(0, 0, 280, 280);

    // Draw grid rings
    for (let ring = 1; ring <= 5; ring++) {
      const r = (ring / 5) * maxRadius;
      ctx.beginPath();
      for (let i = 0; i <= numAxes; i++) {
        const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw axis lines
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(centerX + maxRadius * Math.cos(angle), centerY + maxRadius * Math.sin(angle));
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw data polygon
    ctx.beginPath();
    for (let i = 0; i <= numAxes; i++) {
      const idx = i % numAxes;
      const angle = (Math.PI * 2 * idx) / numAxes - Math.PI / 2;
      const r = (values[idx] / 10) * maxRadius;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.2)');
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw data points
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      const r = (values[i] / 10) * maxRadius;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#3b82f6';
      ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.5)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw labels
    ctx.font = '11px Inter, sans-serif';
    ctx.fillStyle = '#94a3b8';
    ctx.textAlign = 'center';
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      const labelR = maxRadius + 22;
      const x = centerX + labelR * Math.cos(angle);
      const y = centerY + labelR * Math.sin(angle);
      ctx.fillText(labels[i], x, y + 4);
    }
  }, [scores]);

  // Draw score bars
  useEffect(() => {
    if (!barCanvasRef.current || !scores) return;
    const canvas = barCanvasRef.current;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = 300 * dpr;
    canvas.height = 180 * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = '300px';
    canvas.style.height = '180px';

    ctx.clearRect(0, 0, 300, 180);

    const items = [
      { label: 'Technical', value: scores.technical },
      { label: 'Communication', value: scores.communication },
      { label: 'Problem Solving', value: scores.problemSolving },
      { label: 'Experience', value: scores.experience },
      { label: 'Culture Fit', value: scores.cultureFit }
    ];

    const barHeight = 22;
    const gap = 12;
    const startY = 8;
    const maxBarWidth = 160;
    const labelWidth = 110;

    items.forEach((item, i) => {
      const y = startY + i * (barHeight + gap);

      // Label
      ctx.font = '12px Inter, sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.textAlign = 'right';
      ctx.fillText(item.label, labelWidth - 8, y + barHeight / 2 + 4);

      // Background bar
      ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.beginPath();
      ctx.roundRect(labelWidth, y, maxBarWidth, barHeight, 6);
      ctx.fill();

      // Value bar
      const barWidth = (item.value / 10) * maxBarWidth;
      const barGradient = ctx.createLinearGradient(labelWidth, 0, labelWidth + maxBarWidth, 0);
      if (item.value >= 7) {
        barGradient.addColorStop(0, '#2563eb');
        barGradient.addColorStop(1, '#3b82f6');
      } else if (item.value >= 4) {
        barGradient.addColorStop(0, '#f59e0b');
        barGradient.addColorStop(1, '#fbbf24');
      } else {
        barGradient.addColorStop(0, '#dc2626');
        barGradient.addColorStop(1, '#ef4444');
      }
      ctx.fillStyle = barGradient;
      ctx.beginPath();
      ctx.roundRect(labelWidth, y, barWidth, barHeight, 6);
      ctx.fill();

      // Score text
      ctx.font = 'bold 12px Inter, sans-serif';
      ctx.fillStyle = '#f1f5f9';
      ctx.textAlign = 'left';
      ctx.fillText(`${item.value}/10`, labelWidth + maxBarWidth + 8, y + barHeight / 2 + 4);
    });
  }, [scores]);

  if (!scores) return null;

  const getOverallColor = () => {
    if (scores.overall >= 7) return '#3b82f6';
    if (scores.overall >= 4) return '#f59e0b';
    return '#ef4444';
  };

  const getRecColor = () => {
    const rec = scores.recommendation.toLowerCase();
    if (rec.includes('strong hire') || rec === 'pass') return '#3b82f6';
    if (rec.includes('hire')) return '#3b82f6';
    if (rec.includes('maybe')) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ marginBottom: 'var(--space-lg)' }}>
      {/* Overall Score + Recommendation */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-lg)',
        marginBottom: 'var(--space-lg)',
        flexWrap: 'wrap'
      }}>
        {/* Big Score Circle */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <div style={{
            width: '100px',
            height: '100px',
            borderRadius: '50%',
            border: `4px solid ${getOverallColor()}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `${getOverallColor()}15`,
            boxShadow: `0 0 20px ${getOverallColor()}30`
          }}>
            <span style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 800,
              color: getOverallColor()
            }}>
              {scores.overall}
            </span>
            <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>/10</span>
          </div>
          <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            Overall Score
          </span>
        </div>

        {/* Recommendation Badge */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: 'var(--space-sm)'
        }}>
          <div style={{
            padding: 'var(--space-md) var(--space-lg)',
            background: `${getRecColor()}15`,
            border: `2px solid ${getRecColor()}40`,
            borderRadius: 'var(--radius-xl)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Recommendation
            </div>
            <div style={{
              fontSize: 'var(--font-size-xl)',
              fontWeight: 800,
              color: getRecColor(),
              textTransform: 'uppercase'
            }}>
              {scores.recommendation}
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-lg)',
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h4 style={{ marginBottom: 'var(--space-sm)', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Competency Radar
          </h4>
          <canvas ref={radarCanvasRef} />
        </div>
        <div style={{ textAlign: 'center' }}>
          <h4 style={{ marginBottom: 'var(--space-sm)', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Score Breakdown
          </h4>
          <canvas ref={barCanvasRef} />
        </div>
      </div>
    </div>
  );
};

export default ScoreVisualization;
