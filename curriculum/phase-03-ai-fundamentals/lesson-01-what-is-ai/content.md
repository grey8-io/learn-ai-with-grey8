# What is AI? Machine Learning Basics

Welcome to Phase 3! You've got Python skills under your belt, and now it's time to understand the technology you're going to build with. In this lesson, we'll demystify **Artificial Intelligence**, **Machine Learning**, and **Deep Learning** — what they are, how they differ, and how they're used in the real world.

No code in this lesson — just concepts. But don't skip it. A solid understanding of these ideas will make everything that follows click into place.

---

## AI vs ML vs Deep Learning

These terms get thrown around interchangeably, but they mean different things. Think of them as nested circles:

```
  ┌─────────────────────────────────────────┐
  │  Artificial Intelligence                │
  │  ┌───────────────────────────────────┐  │
  │  │  Machine Learning                 │  │
  │  │  ┌─────────────────────────────┐  │  │
  │  │  │  Deep Learning              │  │  │
  │  │  │  (neural networks, LLMs)    │  │  │
  │  │  └─────────────────────────────┘  │  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘
```

**Artificial Intelligence (AI)** is the broadest term. It refers to any system that can perform tasks that would normally require human intelligence — recognizing speech, translating languages, making decisions, playing games. AI includes everything from simple rule-based systems to the most advanced neural networks.

**Machine Learning (ML)** is a subset of AI. Instead of being explicitly programmed with rules, ML systems **learn patterns from data**. You give them examples, and they figure out the rules themselves. This is a fundamental shift: instead of writing "if temperature > 100, then alert," you show the system thousands of examples and let it learn what "abnormal" looks like.

**Deep Learning (DL)** is a subset of ML that uses **neural networks** with many layers (hence "deep"). These networks can learn incredibly complex patterns — they power image recognition, language translation, and the large language models (LLMs) you'll be working with.

Here's an analogy: AI is like "transportation." ML is like "cars" (a specific kind of transportation). Deep Learning is like "electric cars" (a specific kind of car). All electric cars are cars, and all cars are transportation, but not all transportation is a car.

---

## Types of Machine Learning

There are three main approaches to ML, each suited for different problems:

### 1. Supervised Learning

The system learns from **labeled examples** — input-output pairs where the correct answer is known.

**How it works**: You provide training data like "this email is spam" and "this email is not spam." The model learns patterns that distinguish spam from non-spam, then applies those patterns to new emails it hasn't seen before.

**Real-world examples**:
- Email spam detection (spam or not spam)
- Image classification (cat or dog)
- Price prediction (house features → estimated price)
- Medical diagnosis (symptoms → likely condition)

Think of supervised learning like a student studying with an answer key. They see the questions and correct answers, then learn to solve new questions on their own.

### 2. Unsupervised Learning

The system finds **patterns in data without labels** — no correct answers are provided.

**How it works**: You give the system a large dataset and ask it to find structure. It might discover clusters, anomalies, or hidden relationships that humans didn't know existed.

**Real-world examples**:
- Customer segmentation (grouping similar customers)
- Anomaly detection (finding unusual credit card transactions)
- Topic modeling (discovering themes in documents)
- Recommendation systems ("customers who bought X also bought Y")

Think of unsupervised learning like sorting a pile of unlabeled photographs. Nobody tells you the categories — you discover them yourself (landscapes, portraits, food, etc.).

### 3. Reinforcement Learning

The system learns by **taking actions and receiving rewards or penalties** — like training a pet.

**How it works**: An agent interacts with an environment, makes decisions, and receives feedback. Over time, it learns which actions lead to the best outcomes.

**Real-world examples**:
- Game-playing AI (AlphaGo, chess engines)
- Robot navigation (learning to walk or grasp objects)
- Autonomous driving (lane keeping, obstacle avoidance)
- Resource optimization (data center cooling, inventory management)

Think of reinforcement learning like learning to ride a bicycle. Nobody gives you the "correct" movements — you try, fall, adjust, and gradually improve through trial and error.

---

## How Machine Learning Actually Works (Simplified)

At a high level, the ML process follows these steps:

1. **Collect data** — Gather examples relevant to your problem
2. **Prepare data** — Clean it, format it, split it into training and testing sets
3. **Choose a model** — Pick an algorithm suited for your task
4. **Train** — Feed the training data to the model so it learns patterns
5. **Evaluate** — Test the model on data it hasn't seen to measure accuracy
6. **Deploy** — Put the model into production where it makes real predictions

```mermaid
graph LR
    A["Data"] -->|"clean & split"| B["Prepare"]
    B -->|"fit the model"| C["Train"]
    C -->|"test on new data"| D["Evaluate"]
    D -->|"serve to users"| E["Deploy"]
```

The magic happens in step 4: the model adjusts its internal parameters to minimize errors. The more data and the better the data, the better the model performs.

---

## Where Does ChatGPT Fit In?

ChatGPT and similar AI assistants are products of **deep learning** — specifically, they're **large language models** (LLMs). They were trained on massive amounts of text using a combination of supervised and reinforcement learning. We'll dive deep into how LLMs work in the next lesson.

For now, understand that when you chat with an LLM, you're interacting with a model that has learned statistical patterns in language. It doesn't "understand" in the way humans do — it predicts what words should come next based on patterns it learned during training.

---

## Why This Matters for You

As an AI developer, you don't need to build ML models from scratch (unless you want to). Your job is typically to:

- **Choose the right tool** for the problem
- **Call pre-trained models** through APIs
- **Prepare data** effectively
- **Evaluate results** critically
- **Build applications** that use AI responsibly

Understanding the fundamentals helps you make better decisions about when AI is the right solution, which approach to use, and what limitations to expect.

---

## Your Turn

In the exercise that follows, you'll practice classifying ML problems. Given descriptions of real-world scenarios, you'll determine whether each one is a supervised, unsupervised, or reinforcement learning problem. This skill — matching problems to approaches — is something you'll use throughout your AI career.

Let's test your understanding!
