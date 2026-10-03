# Generative and Agentic AI in Production

Practice repo for deploying generative and agentic AI. Course instructions stay in `production/`. Apps, notes, and deployment records built while following the course go in their own directories at the repo root, so the course material stays unchanged.

## Course

- [Udemy course](https://external-teksystems.udemy.com/course/generative-and-agentic-ai-in-production/learn/lecture/52441427?start=75#overview)
- Upstream materials: [ed-donner/production](https://github.com/ed-donner/production)
- [Course resources and slides](https://edwarddonner.com/2025/09/15/ai-in-production-gen-ai-and-agentic-ai-on-aws-at-scale/)

Start at [`production/week1/day1.md`](production/week1/day1.md). Setup guides are in [`production/guides`](production/guides/01_intro.ipynb).

## Layout

| Path | What it is |
| --- | --- |
| `production/` | Day-by-day course instructions, copied from the upstream repo. Follow these; do not turn them into the project code. |
| Project directories at the repo root | Apps built during the course (SaaS, digital twin, AgentCore experiments). Add each one when that part of the course starts. |

## Work in this repo

**Week 1 — a small AI SaaS.** Deploy a FastAPI app to Vercel, then build a Next.js and FastAPI product with Clerk authentication and billing. Finish by containerizing a healthcare consultation assistant and deploying it to AWS Lambda.

**Week 2 — an AI digital twin.** Build a conversational twin with memory, deploy it on AWS (Lambda, S3, API Gateway, CloudFront), switch the model to Amazon Bedrock, then manage the infrastructure with Terraform and ship it with GitHub Actions.

**Weeks 3 and 4 — security and multi-agent work.** The course leaves this material and continues in [ed-donner/cyber](https://github.com/ed-donner/cyber) and [ed-donner/alex](https://github.com/ed-donner/alex). Keep notes and links for that work here; the applications themselves live in those repos.

**Finale — Amazon Bedrock AgentCore.** Follow [`production/finale`](production/finale/README.md) to run a Strands agent on AgentCore. Code for that exercise can live beside the finale instructions or in a root-level project directory.

## Practices

- Do not commit `.env` files, AWS credentials, or Clerk secrets.
- When the upstream course repo changes, update `production/` from [ed-donner/production](https://github.com/ed-donner/production) instead of editing the instructions in place.
