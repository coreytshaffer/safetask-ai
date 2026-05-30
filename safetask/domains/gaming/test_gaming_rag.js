const fs = require('fs');
const path = require('path');

// Mock DOM elements or globals
let regulationsDatabase = [];

function loadRegulations() {
  const regPath = path.normalize(path.join(__dirname, 'regulations.json'));
  if (!regPath.startsWith(__dirname)) {
    throw new Error("Invalid path");
  }
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
      input: "dealer failed to clear hands at blackjack table 4",
      expectedCodes: ["SICS Section 3.1.4"]
    },
    {
      input: "patron faked a slip and fall in liquid near the slot machine bank",
      expectedCodes: ["Legal & Risk Policy: Constructive Knowledge"]
    },
    {
      input: "unauthorized access to the main cage vault and door propped open",
      expectedCodes: ["NIGC MICS 25 CFR § 543.21"]
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
