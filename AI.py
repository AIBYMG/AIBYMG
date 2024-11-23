import discord
import sqlite3
from discord.ext import commands

# Funkcja do połączenia z bazą danych
def connect_db():
    return sqlite3.connect("chatbot.db")

# Funkcja do załadowania wiedzy z bazy danych
def load_knowledge():
    conn = connect_db()
    c = conn.cursor()

    # Tworzymy tabelę knowledge, jeśli nie istnieje
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
                    question TEXT PRIMARY KEY,
                    answer TEXT NOT NULL)''')

    c.execute("SELECT question, answer FROM knowledge")
    knowledge = c.fetchall()
    conn.close()

    return {q: a for q, a in knowledge}

# Funkcja do zapisania nowej wiedzy do bazy danych
def save_knowledge(question, answer):
    conn = connect_db()
    c = conn.cursor()

    # Wstawiamy nową odpowiedź lub aktualizujemy istniejącą
    c.execute("REPLACE INTO knowledge (question, answer) VALUES (?, ?)", (question, answer))

    conn.commit()
    conn.close()
# Funkcja odpowiadająca na zapytanie
def get_response(user_input, knowledge):
    user_input = user_input.lower()

    # Jeśli użytkownik pyta o coś, czego chatbot się nauczył
    if user_input in knowledge:
        return knowledge[user_input]

    # Jeśli chatbot nie zna odpowiedzi
    return "Przepraszam, nie wiem odpowiedzi na to pytanie. Czy chcesz, żebym się tego nauczył? (tak/nie)"

# Funkcja uczenia się (dodaje nowe odpowiedzi do bazy danych)
def learn_from_user(question, answer, knowledge):
    save_knowledge(question, answer)
    knowledge[question.lower()] = answer
    return f"Teraz wiem, że '{question}' to '{answer}'. Dzięki za naukę!"

# Funkcja edytowania odpowiedzi na już zapisane pytanie
def edit_answer(question, knowledge):
    new_answer = input(f"Podaj nową odpowiedź na pytanie '{question}': ").strip()
    save_knowledge(question, new_answer)
    knowledge[question] = new_answer
    return f"Odpowiedź na '{question}' została zaktualizowana!"

# Funkcja przypisywania odpowiedzi z jednego pytania do innego
def copy_answer_to_new_question(from_question, to_question, knowledge):
    # Sprawdzamy, czy pytanie źródłowe istnieje w bazie danych
    if from_question in knowledge:
        # Przypisujemy odpowiedź z pytania źródłowego do nowego pytania
        save_knowledge(to_question, knowledge[from_question])
        knowledge[to_question] = knowledge[from_question]
        return f"Odpowiedź na '{to_question}' została przypisana z '{from_question}'."
    else:
        return f"Nie znam odpowiedzi na pytanie '{from_question}', więc nie mogę przypisać odpowiedzi."

# Tworzenie obiektu bota
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ładowanie wiedzy na starcie
knowledge = load_knowledge()

# Komenda do nauki chatbota
@bot.command(name='naucz')
async def learn(ctx, question: str, *, answer: str):
    learn_from_user(question, answer, knowledge)
    await ctx.send(f"Chatbot nauczył się, że '{question}' to '{answer}'.")

# Komenda do przypisania odpowiedzi z jednego pytania do innego
@bot.command(name='przypisz')
async def copy_answer(ctx, from_question: str, to_question: str):
    result = copy_answer_to_new_question(from_question.lower(), to_question.lower(), knowledge)
    await ctx.send(result)

# Komenda do edytowania odpowiedzi
@bot.command(name='edytuj')
async def edit(ctx, question: str, *, new_answer: str):
    if question.lower() in knowledge:
        save_knowledge(question.lower(), new_answer)
        knowledge[question.lower()] = new_answer
        await ctx.send(f"Odpowiedź na '{question}' została zaktualizowana na '{new_answer}'.")
    else:
        await ctx.send(f"Chatbot nie zna odpowiedzi na '{question}'.")

# Komenda do uzyskania odpowiedzi
@bot.command(name='pytanie')
async def question(ctx, *, user_input: str):
    response = get_response(user_input, knowledge)
    await ctx.send(response)

# Uruchomienie bota
bot.run('MTMwOTg1Njg0MzkxNjM3ODI1NA.Gtgml0.gNdCurXO483-CS5S3_e9tdHqc9QVNQ5fJRHCLM')
