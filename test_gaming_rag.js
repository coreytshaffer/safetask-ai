const fs = require('fs');
const path = require('path');

// Mock DOM elements or globals
let regulationsDatabase = [];

function loadRegulations() {
  const regPath = path.join(__dirname, 'regulations.json');
  const data = fs.readFileSync(regPath, 'utf8');
  regulationsDatabase = JSON.parse(data);
  console.log(`Loaded ${regulationsDatabase.length} regulations for testing.`);
}

function scanRegulations(inputText) {
  if (!inputText || inputText.trim().length < 5) {
    return [];
  }

  const cleanedText = inputText.toLowerCase();
  const matched = [];

  regulationsDatabase.forEach(reg => {
    let matchScore = 0;
    reg.keywords.forEach(keyword => {
      if (cleanedText.includes(keyword)) {
        matchScore++;
      }
    });

    if (matchScore > 0) {
      matched.push({
        code: reg.code,
        title: reg.title,
        score: matchScore
      });
    }
  });

  matched.sort((a, b) => b.score - a.score);
  return matched;
}

// Run Test Cases
try {
  loadRegulations();
  
  const testCases = [
    {
      input: "working at heights of 10 feet to repair roof vents on a ladder",
      expectedCodes: ["Title 8 CCR §1670"]
    },
    {
      input: "working in an outdoor farm during a hot dry summer day with high temperature",
      expectedCodes: ["Title 8 CCR §3395"]
    },
    {
      input: "clearing brush near a wildfire with heavy smoke and haze in the air",
      expectedCodes: ["Title 8 CCR §5141.1"]
    },
    {
      input: "digging a deep excavation ditch trench for plumbing pipes",
      expectedCodes: ["Title 8 CCR §1541"]
    },
    {
      input: "troubleshooting high voltage electrical wire line in a live cabinet LOTO",
      expectedCodes: ["Title 8 CCR §2320.2"]
    }
  ];

  let passed = 0;
  testCases.forEach((tc, idx) => {
    console.log(`\n---------------------------------------------\nTest Case ${idx + 1}: "${tc.input}"`);
    const results = scanRegulations(tc.input);
    console.log("Matched Standards:", results.map(r => `${r.code} (Score: ${r.score})`));
    
    // Check if expected codes are in matched list
    const matchedCodes = results.map(r => r.code);
    const hasExpected = tc.expectedCodes.every(code => matchedCodes.includes(code));
    
    if (hasExpected) {
      console.log("✓ PASS");
      passed++;
    } else {
      console.log(`✗ FAIL: Expected to find [${tc.expectedCodes.join(', ')}], got [${matchedCodes.join(', ')}]`);
    }
  });

  console.log(`\n=============================================\nVerification complete: ${passed}/${testCases.length} tests passed.`);
  process.exit(passed === testCases.length ? 0 : 1);

} catch (error) {
  console.error("Verification error:", error);
  process.exit(1);
}
