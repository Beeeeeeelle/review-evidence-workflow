const assert = require('node:assert/strict');
const {locate} = require('../review-evidence-workflow/assets/evidence-reader.js');
const words = [
 {text:'Self-',line:1,x:.1,y:.2,w:.1,h:.02},
 {text:'regulated',line:2,x:.1,y:.3,w:.2,h:.02},
 {text:'learning',line:2,x:.31,y:.3,w:.1,h:.02},
 {text:'supports',line:2,x:.42,y:.3,w:.1,h:.02},
 {text:'agency.',line:2,x:.53,y:.3,w:.1,h:.02}
];
assert.equal(locate(words,'Self-regulated learning supports agency.').status,'matched');
assert.equal(locate(words,'Self regulated learning supports agency').boxes.length,2);
assert.equal(locate(words,'Self-regulated learning destroys agency').status,'unmatched');
assert.equal(locate(words,'regulated learning support').status,'unmatched');
assert.equal(locate([...words,...words],'Self regulated learning supports agency').status,'ambiguous');
assert.equal(locate([], 'Self regulated learning').status,'unmatched');
assert.equal(locate(words, 'agency').status,'unmatched');
assert.equal(locate([{text:'ﬁndings',line:1,x:.1,y:.2,w:.2,h:.02},{text:'reported',line:1,x:.31,y:.2,w:.2,h:.02}], 'findings reported').status,'matched');
console.log('Reader checks passed: line breaks, hyphens, ligatures, no fuzzy matching, ambiguity, missing text and short quotes.');
