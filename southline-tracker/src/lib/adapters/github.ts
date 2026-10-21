// Opens GitHub issues for change requests made in the app. The repo's
// .github/workflows/claude.yml wakes Claude on issues that mention @claude;
// Claude implements the change and opens a pull request for you to approve.
//
// Env: GITHUB_TOKEN (fine-grained token with Issues: read & write on the repo)
//      GITHUB_REPO  ("owner/repo", e.g. orourkeryan88-byte/school-work)

import { secret } from "@/lib/secrets";

export async function githubConfigured() {
  return Boolean((await secret("GITHUB_TOKEN")) && (await secret("GITHUB_REPO")));
}

export async function createIssue(title: string, body: string, labels: string[], fetchImpl: typeof fetch = fetch): Promise<{ url: string; number: number }> {
  const [token, repo] = [await secret("GITHUB_TOKEN"), await secret("GITHUB_REPO")];
  const res = await fetchImpl(`https://api.github.com/repos/${repo}/issues`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title, body, labels }),
    signal: AbortSignal.timeout(15000),
  });
  // A token without label permission gets a 422 for labels - retry without them.
  if (res.status === 422 && labels.length) return createIssue(title, body, [], fetchImpl);
  if (!res.ok) throw new Error(`GitHub ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const data = (await res.json()) as { html_url: string; number: number };
  return { url: data.html_url, number: data.number };
}
