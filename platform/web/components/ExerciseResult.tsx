interface TestResult {
  name: string;
  passed: boolean;
  message?: string;
}

interface GradeResult {
  score: number;
  passed: boolean;
  tests: TestResult[];
  feedback: string;
}

interface ExerciseResultProps {
  result: GradeResult;
  attemptCount?: number;
}

/** Clean up test name: "test_exercise.py::test_greet_returns_correct_string" → "greet returns correct string" */
function cleanTestName(raw: string): string {
  let name = raw;
  // Remove file prefix
  if (name.includes("::")) name = name.split("::").pop() || name;
  // Remove "test_" prefix
  if (name.startsWith("test_")) name = name.slice(5);
  // Replace underscores with spaces
  name = name.replace(/_/g, " ");
  return name;
}

export default function ExerciseResult({ result, attemptCount }: ExerciseResultProps) {
  const tests = result.tests ?? [];
  const failedTests = tests.filter((t) => !t.passed);
  const passedTests = tests.filter((t) => t.passed);
  const totalTests = tests.length;
  const passedCount = passedTests.length;

  return (
    <div
      className={`rounded-xl border p-4 ${
        result.passed
          ? "border-emerald-600/30 bg-emerald-600/5"
          : "border-red-600/30 bg-red-600/5"
      }`}
    >
      {/* Score header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          {result.passed ? (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-600/20 text-emerald-400">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
            </div>
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-600/20 text-red-400">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </div>
          )}
          <div>
            <h3 className="text-sm font-semibold text-slate-100">
              {result.passed
                ? "All Tests Passed!"
                : `${passedCount}/${totalTests} Tests Passed`}
            </h3>
            <p className="text-xs text-slate-400">
              Score: {result.score}%
              {attemptCount !== undefined && attemptCount > 1 && (
                <span className="ml-2">Attempt #{attemptCount}</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Score bar */}
      <div className="h-2 w-full rounded-full bg-slate-700 mb-4">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            result.score >= 80
              ? "bg-emerald-500"
              : result.score >= 50
              ? "bg-amber-500"
              : "bg-red-500"
          }`}
          style={{ width: `${result.score}%` }}
        />
      </div>

      {result.passed ? (
        <>
          {/* Success: show passed tests + AI feedback */}
          {passedTests.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-medium text-emerald-400 mb-2 uppercase tracking-wide">
                Passed ({passedTests.length})
              </p>
              <div className="space-y-1">
                {passedTests.map((test, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <svg className="h-3.5 w-3.5 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                    <span className="text-slate-400 text-xs">
                      {cleanTestName(test.name)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.feedback && (
            <div className="rounded-lg bg-slate-800/50 p-3">
              <p className="text-xs font-medium text-slate-400 mb-1">
                AI Feedback
              </p>
              <p className="text-sm text-slate-300 leading-relaxed">
                {result.feedback}
              </p>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Failure: show failed tests + guidance, AI feedback only for partial passes */}
          {failedTests.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-medium text-red-400 mb-2 uppercase tracking-wide">
                Failed ({failedTests.length})
              </p>
              <div className="space-y-2">
                {failedTests.map((test, i) => (
                  <div
                    key={i}
                    className="rounded-lg border border-red-500/20 bg-red-500/5 p-3"
                  >
                    <div className="flex items-start gap-2">
                      <svg className="h-4 w-4 shrink-0 text-red-400 mt-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                      </svg>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-red-300">
                          {cleanTestName(test.name)}
                        </p>
                        {test.message && test.message !== "Test FAILED" && test.message !== "Test ERROR" && (
                          <p className="mt-1 text-xs text-red-200/70 font-mono break-all">
                            {test.message}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Passed tests — compact, shown only when some passed */}
          {passedTests.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-medium text-emerald-400 mb-2 uppercase tracking-wide">
                Passed ({passedTests.length})
              </p>
              <div className="space-y-1">
                {passedTests.map((test, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <svg className="h-3.5 w-3.5 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                    <span className="text-slate-400 text-xs">
                      {cleanTestName(test.name)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Smart guidance */}
          {failedTests.length > 0 && (
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 mb-4">
              <div className="flex items-start gap-2">
                <svg className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
                </svg>
                <div className="text-xs text-amber-200/80">
                  <p className="font-medium text-amber-300 mb-1">What to try next:</p>
                  {(() => {
                    const allMessages = failedTests.map((t) => t.message || "").join(" ");
                    const hasTypeError = allMessages.includes("TypeError");
                    const hasSyntaxError = allMessages.includes("SyntaxError");
                    const hasNameError = allMessages.includes("NameError");
                    const hasKeyError = allMessages.includes("KeyError");
                    const hasAttributeError = allMessages.includes("AttributeError");
                    const returnsNone = /isinstance\(None/.test(allMessages) || /assert None/.test(allMessages);
                    const hasIndentationError = allMessages.includes("IndentationError");
                    const sameError = failedTests.length > 1 &&
                      failedTests.every((t) => t.message === failedTests[0].message);

                    // Pattern: function exists but returns None + KeyErrors on expected args
                    // → code is likely written outside the function body
                    const emptyFunctionBody = (returnsNone || hasKeyError) &&
                      passedTests.some((t) => /exists|defined|callable/.test(t.name));

                    if (emptyFunctionBody) {
                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          <li>Your function <strong>exists</strong> but isn&apos;t doing anything — make sure your code is <strong>indented inside the function body</strong>, not written below it at the module level</li>
                          {returnsNone && (
                            <li>The function is returning <code className="bg-slate-700/50 px-1 rounded text-amber-300">None</code> — it needs a <code className="bg-slate-700/50 px-1 rounded text-amber-300">return</code> statement with the result</li>
                          )}
                          {hasKeyError && (
                            <li>The tests can&apos;t find expected values because the function body is empty — move your code inside the function</li>
                          )}
                        </ul>
                      );
                    }

                    // Pattern: TypeError/SyntaxError/NameError — specific runtime errors
                    if (hasTypeError || hasSyntaxError || hasNameError || hasIndentationError) {
                      const typeMatch = allMessages.match(/not "(\w+)"/);
                      const wrongType = typeMatch ? typeMatch[1] : null;

                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          {sameError && (
                            <li>All tests hit the <strong>same error</strong> — fix that one issue and they should all pass</li>
                          )}
                          {hasTypeError && wrongType === "set" && (
                            <li><strong>TypeError (set)</strong> — curly braces <code className="bg-slate-700/50 px-1 rounded text-amber-300">{"{variable}"}</code> create a <em>set</em> in Python, not a string substitution. Use an <strong>f-string</strong>: <code className="bg-slate-700/50 px-1 rounded text-amber-300">f&quot;text {"{variable}"}&quot;</code> (note the <code className="bg-slate-700/50 px-1 rounded text-amber-300">f</code> prefix before the quote)</li>
                          )}
                          {hasTypeError && wrongType === "int" && (
                            <li><strong>TypeError (int)</strong> — you&apos;re using <code className="bg-slate-700/50 px-1 rounded text-amber-300">+</code> between a string and a number. Convert with <code className="bg-slate-700/50 px-1 rounded text-amber-300">str()</code> or use an f-string: <code className="bg-slate-700/50 px-1 rounded text-amber-300">f&quot;text {"{number}"}&quot;</code></li>
                          )}
                          {hasTypeError && wrongType && wrongType !== "set" && wrongType !== "int" && (
                            <li><strong>TypeError ({wrongType})</strong> — you&apos;re mixing a string with a <code className="bg-slate-700/50 px-1 rounded text-amber-300">{wrongType}</code>. Use an f-string or convert the value with <code className="bg-slate-700/50 px-1 rounded text-amber-300">str()</code></li>
                          )}
                          {hasTypeError && !wrongType && (
                            <li><strong>TypeError</strong> means you&apos;re mixing incompatible types — use an f-string or <code className="bg-slate-700/50 px-1 rounded text-amber-300">str()</code> to convert values</li>
                          )}
                          {hasSyntaxError && (
                            <li><strong>SyntaxError</strong> means Python can&apos;t parse your code — check for missing colons, unmatched quotes, or indentation</li>
                          )}
                          {hasIndentationError && (
                            <li><strong>IndentationError</strong> — Python uses indentation to define blocks. Make sure the code inside your function is indented with 4 spaces</li>
                          )}
                          {hasNameError && (
                            <li><strong>NameError</strong> means a variable or function isn&apos;t defined — check for typos or make sure you defined it before using it</li>
                          )}
                          <li>Read the error message above carefully — it tells you the exact line and what went wrong</li>
                        </ul>
                      );
                    }

                    // Pattern: function returns None without other errors
                    if (returnsNone) {
                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          <li>Your function is returning <code className="bg-slate-700/50 px-1 rounded text-amber-300">None</code> — make sure it has a <code className="bg-slate-700/50 px-1 rounded text-amber-300">return</code> statement that sends back the result</li>
                          <li>Check that your logic is <strong>inside the function body</strong> (indented), not written below it</li>
                        </ul>
                      );
                    }

                    // Pattern: KeyError — tests expect certain keys/values
                    if (hasKeyError) {
                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          <li><strong>KeyError</strong> means the tests expected certain keys or values that weren&apos;t found — check that your code produces the right data structure</li>
                          <li>Make sure your code is <strong>inside the function body</strong> so it runs when the tests call the function</li>
                          <li>Use a <strong>Hint</strong> if you&apos;re unsure what the function should return</li>
                        </ul>
                      );
                    }

                    // Pattern: AttributeError — calling method on wrong type
                    if (hasAttributeError) {
                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          <li><strong>AttributeError</strong> — you&apos;re calling a method on an object that doesn&apos;t have it. Check that variables hold the type you expect</li>
                          <li>Read the error message above to see which attribute is missing and on which object</li>
                        </ul>
                      );
                    }

                    // Pattern: few failures with assertion details
                    if (failedTests.length <= 2) {
                      return (
                        <ul className="space-y-0.5 list-disc list-inside">
                          <li>Read the failed test names — they describe exactly what&apos;s expected</li>
                          {failedTests.some((t) => t.message && t.message.includes("assert")) && (
                            <li>Check the error details above — they show expected vs actual values</li>
                          )}
                          <li>Use a <strong>Hint</strong> if you&apos;re stuck on the approach</li>
                          <li>Ask the <strong>AI Tutor</strong> for guidance without spoiling the answer</li>
                        </ul>
                      );
                    }

                    // Fallback: many failures, no specific pattern detected
                    return (
                      <ul className="space-y-0.5 list-disc list-inside">
                        <li>Multiple tests are failing — re-read the lesson content for the core concepts</li>
                        <li>Start with the simplest failing test and fix one at a time</li>
                        <li>Use <strong>Hint Level 1</strong> for a gentle nudge in the right direction</li>
                        <li>The <strong>AI Tutor</strong> can help you break the problem down</li>
                      </ul>
                    );
                  })()}
                </div>
              </div>
            </div>
          )}

          {/* AI Feedback — only show on partial pass (some tests passed) for targeted advice */}
          {result.feedback && passedTests.length > 0 && (
            <div className="rounded-lg bg-slate-800/50 p-3">
              <p className="text-xs font-medium text-slate-400 mb-1">
                AI Feedback
              </p>
              <p className="text-sm text-slate-300 leading-relaxed">
                {result.feedback}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
