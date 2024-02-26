from openai import OpenAI
import asyncio
import json
import os
import tiktoken

import json

def load_api_key(key="None"):
    with open('config.json') as f:
        config = json.load(f)
    if key == "llm":
        return config['OPENAI_API_KEY']
    if key == "discord":
        return config['DISCORD_API_KEY']

async def llm_completion(model,messages):
    api_key = load_api_key("llm")
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=messages
      )
    return completion

def num_tokens_from_string(string: str, encoding_name="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
    
async def check_if_called(user_message):
    model = "gpt-3.5-turbo"
    messages = [
      {"role": "system", "content": "You are a helpful assistant named 'Abraxsas' sometimes mispelled 'Abrasax' among other typos. You monitor a group chat for if you have been summoned for a task in chat. You know you have been summoned if a request is asked of you directly and you were mentioned by name. Never if a request or question is aimed at someone else or it is unclear"},
      {"role": "system", "content": "If it appears you specifically were summoned by name, and were asked for trivia, return 'trivia' only"},
      {"role": "system", "content": "If it appears you specifically were summoned to answer a question, return 'generalQA' only"},
      {"role": "system", "content": "If it appears you specifically were summoned but you are unsure for what return 'unsure'"},
      {"role": "system", "content": "If it does not appear you specifically were summoned return 'false' only"},
      {"role": "user", "content": f"{user_message}"}
    ]
    call_status = await llm_completion(model=model, messages=messages)
    
    return call_status

async def trivia_module(message, client, timeout=60):
    # Load previous questions
    if os.path.exists('question_history.json'):
        with open('question_history.json', 'r') as f:
            question_history = json.load(f)
    else:
        question_history = []

    completion = await llm_completion(model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant. You will be asked to provide a trivia question, you should only reply with only the trivia question and nothing else"},
                                    {"role": "user", "content": "Please come up with an interesting trivia question suitable to a group of diverse adults who are gathered over a joint love of nerd culture and board games"}
                                    ]
                                 )
    question = completion.choices[0].message.content.strip()

    # Add new question to history and save
    question_history.append(question)
    with open('question_history.json', 'w') as f:
        json.dump(question_history, f)

    question_message = await message.channel.send(f'Here is your question: {question}')
    anscompletion = await llm_completion(model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant. You ask trivia and answer questions."},
                                    {"role": "user", "content": f"Please tell us the answer to {question}! you should provide the answer in past tense, and without additional explanations, e.g. 'the answer was ....'"}
                                    ]
                                 )
    correct_answer = anscompletion.choices[0].message.content.strip()
    # Wait for a reply to the question message
    def check(m):
        return m.reference is not None and m.reference.message_id == question_message.id
 
    user_scores = {}
    
    try:
        while True:
            answer = await client.wait_for('message', check=check, timeout=timeout)
            rating = await llm_completion(model="gpt-4",
                                          messages=[
                                              {"role": "system", "content": "You are a helpful, affable and energetic assistant! :) You help rate trivia answers. You should award from 5 up to 10 points for a correct answer, from 0 up to 5 points for a creative incorrect answer, and from 0 up to 5 points for a funny answer. You answer or 'scoring' should be given as a python syntax dictionary following the format {\"Username\":\"Username\", Score\": NumericalScore, \"Comment\": \"A very short, few word rationale For Score\"} you should return this dictionary and nothing else"},
                                              {"role": "user", "content": f"The question was {question} and the answer from {answer.author.name} was {answer.content} please provide a scoring"}
                                              ]
                                          )
            score = rating.choices[0].message.content.strip()
            user_scores[answer.author.name] = json.loads(score)
            #return user_scores
    except asyncio.TimeoutError:
        table = f"{str("User").ljust(15)}| {str("Score").ljust(5)} | Note\n"
        table += "\n"
        for user, score in user_scores.items():
            table += f"{user.ljust(15)}| {str(score['Score']).ljust(5)} | {score['Comment']}\n"
        print(table)
        await message.channel.send(f'Final Scores\n```{table}```\n{correct_answer}')
    return user_scores

async def generalqa_module(message, client, timeout=15):
    completion = await llm_completion(model="gpt-4",
                                messages=[
                                    {"role": "system", "content": f"You are Abraxsas, a helpful assistant that interacts with a diverse group of adults who are gathering around mutual interest in board games, cosplay and general nerd culture. You are friendly, helpful energetic and affable. The user {message.author} has sent you a question"},
                                    {"role": "user", "content": f"{message.content}"}
                                    ]
                                 )
    answer = completion.choices[0].message.content.strip()
    await message.channel.send(f'{answer}')
