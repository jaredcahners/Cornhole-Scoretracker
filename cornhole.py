import sqlite3
from tkinter import *
from PIL import ImageTk,Image
import pandas as pd

conn = sqlite3.connect('ch.sqlite')
cur = conn.cursor()

#making the database

cur.execute('''
            CREATE TABLE IF NOT EXISTS Innings
            (inning_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            month TEXT NOT NULL,
            cornholes INTEGER,
            woodies INTEGER,
            total_score INTEGER
             )
             ''')

conn.commit

ch_num = 0
w_num = 0
total = 0

def cornhole():
    '''Destroys count labels
    Adds 1 cornhole and 3 points to total
    New values to count labels'''
    global ch_num
    global w_num
    global total
    global ch_count
    global w_count
    global total_count

    ch_count.destroy()
    w_count.destroy()
    total_count.destroy()

    ch_num = ch_num + 1
    total = total + 3
    ch_count = Label(enterscores, text=ch_num)
    ch_count.grid(row=3, column=0, padx=10, pady=10)
    w_count = Label(enterscores, text=w_num)
    w_count.grid(row=3, column=1, padx=10, pady=10)
    total_count = Label(enterscores, text=total)
    total_count.grid(row=3, column=2, padx=10, pady=10)

def woody():
    '''Destroys count labels
    Adds 1 woody and 1 point to total
    New values to count labels'''
    global ch_num
    global w_num
    global total
    global ch_count
    global w_count
    global total_count

    ch_count.destroy()
    w_count.destroy()
    total_count.destroy()

    w_num = w_num + 1
    total = total + 1
    ch_count = Label(enterscores, text=ch_num)
    ch_count.grid(row=3, column=0, padx=10, pady=10)
    w_count = Label(enterscores, text=w_num)
    w_count.grid(row=3, column=1, padx=10, pady=10)
    total_count = Label(enterscores, text=total)
    total_count.grid(row=3, column=2, padx=10, pady=10)

def clear():
    '''Destroys count labels
    makes counts 0
    New values to labels'''
    global ch_num
    global w_num
    global total
    global ch_count
    global w_count
    global total_count

    ch_count.destroy()
    w_count.destroy()
    total_count.destroy()

    ch_num = 0
    w_num = 0
    total = 0

    ch_count = Label(enterscores, text=ch_num)
    ch_count.grid(row=3, column=0, padx=10, pady=10)
    w_count = Label(enterscores, text=w_num)
    w_count.grid(row=3, column=1, padx=10, pady=10)
    total_count = Label(enterscores, text=total)
    total_count.grid(row=3, column=2, padx=10, pady=10)

def enter():
    '''Enters new round into Database
    if lacks information tells user and doesn't entered
    clears labels'''
    global enterLabel
    if not name.get() or not month.get():
        enterLabel = Label(enterscores, text="Enter a name and a month please! (Inning not entered)")
        enterLabel.grid(row=5, column=0, columnspan=2)
    else:
        enterLabel.destroy()
        enterLabel = Label(enterscores, text=name.get()+" "+str(ch_num)+"/"+str(w_num)+" = "+str(total)+" Entered!")
        enterLabel.grid(row=5, column=0, columnspan=2)

        cur.execute('''
            INSERT INTO Innings (name, month, cornholes, woodies, total_score)
            VALUES ( ? , ? , ? , ? , ? )''', (name.get(), month.get(), ch_num, w_num, total))

        conn.commit()

        global ch_count
        global w_count
        global total_count

        ch_count.destroy()
        w_count.destroy()
        total_count.destroy()

        if name.get() not in name_list:
            name_list.append(name.get())
        clear()

def fullreport():
    "Sends database to excel"
    df = pd.read_sql_query('''  SELECT *
                                FROM Innings
                                ORDER BY month, name, total_score DESC''', conn)
    df.to_excel(r'FullReport.xlsx', index=False, header=True)

def showmonthhigh():
    '''Queries database for best scores in a months
    Displays in label'''

    query = cur.execute( '''    SELECT name
                            ,cornholes
                            ,woodies
                            ,total_score
                        FROM Innings
                        WHERE month = ?
                        ORDER BY total_score DESC, cornholes DESC, name
                        LIMIT 10''', (highmonth.get(), ))

    cols = ["Name", "Cornholes", "Woodies", "Total"]
    showmonthhigh_df = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

    global reportspace
    if len(showmonthhigh_df.index) == 0:
        reportspace = Label(root, text = "There were no innings played in " + highmonth.get()+"!")
        reportspace.grid(row=4, column=0)
    else:
        reportspace = Label(root, text = showmonthhigh_df.to_string(index=False))
        reportspace.grid(row=4, column=0)

def showmonthhighfive():
    '''Queries database for top 5 rounds per player in a months
    returns Player and Average
    creates dataframe from that name_list
    displays dataframe in label'''

    highfives = []
    for name in name_list:

        cur.execute( '''

                                SELECT name
                                    ,AVG(total_score)
                                FROM
                                (SELECT name
                                    ,total_score
                                FROM Innings
                                WHERE month = ? AND
                                    name = ?
                                ORDER BY total_score DESC
                                LIMIT 5)
                                GROUP BY name
                                ''', (highfivemonth.get(), name)
                                )

        rec = cur.fetchone()
        if rec is not None:
            highfives.append(rec)
    highfives_df = pd.DataFrame(data=highfives, columns=["Name", "Top Five Avg"])
    highfives_df.sort_values(by=['Top Five Avg'], inplace=True, ascending=False)

    global reportspace

    if len(highfives_df.index) == 0:
        reportspace = Label(root, text = "There were no innings played in " + highfivemonth.get()+"!")
        reportspace.grid(row=4, column=0)
    else:
        reportspace = Label(root, text = highfives_df.to_string(index=False))
        reportspace.grid(row=4, column=0)


def clearreport():
    '''Empties the report sp[ace label'''
    global reportspace
    reportspace.destroy()

root = Tk()
root.title("Cornhole Score Logger")

enterscores = LabelFrame(root, text="Enter Innings")
enterscores.grid(row=0, column=0, padx=20, pady=20)

nameLabel = Label(enterscores, text="Name: ")
nameLabel.grid(row=0, column=0, padx=10, pady=10)
name = Entry(enterscores, width=20)
name.grid(row=0, column=1, padx=10, pady=10)
monthLabel = Label(enterscores, text="Month: ")
monthLabel.grid(row=0, column=2, padx=10, pady=10)
month = StringVar()
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
monthMenu = OptionMenu(enterscores, month, *months)
monthMenu.grid(row=0, column=3, padx=10, pady=10)

playersFrame=LabelFrame(enterscores, text="Players Already In Database")
playersFrame.grid(row=1, column=0)

cornhole_button=Button(enterscores, text="Cornholes", command=cornhole)
cornhole_button.grid(row=2, column=0, padx=10, pady=10)
woody_button=Button(enterscores, text="Woodies", command=woody)
woody_button.grid(row=2, column=1, padx=10, pady=10)
totalscoreLabel = Label(enterscores, text="Total Score")
totalscoreLabel.grid(row=2, column=2, padx=10, pady=10)

ch_count = Label(enterscores, text="     ")
ch_count.grid(row=3, column=0, padx=10, pady=10)
w_count = Label(enterscores, text="     ")
w_count.grid(row=3, column=1, padx=10, pady=10)
total_count = Label(enterscores, text="     ")
total_count.grid(row=3, column=2, padx=10, pady=10)

enterButton=Button(enterscores, text="Enter Inning", command=enter, padx=175)
enterButton.grid(row=4, column=0, columnspan=2)
enterLabel = Label(enterscores, text="     ")
enterLabel.grid(row=5, column=0, columnspan=2)
clearButton=Button(enterscores, text="Clear Inning", command=clear)
clearButton.grid(row=4, column=2)

name_list = []
for row in cur.execute('SELECT DISTINCT name FROM Innings'):
    name_list.append(''.join(row))

playersLabel=Label(playersFrame, text=name_list, padx=20)
playersLabel.grid(row=0, column=0)

reportsFrame=LabelFrame(root, text="Reports")
reportsFrame.grid(row=3, column=0)

fullreportButton=Button(reportsFrame, text="Full Report (to Excel)", command=fullreport)
fullreportButton.grid(row=0, column=0)

monthlyhighFrame=LabelFrame(reportsFrame, text="Monthly High Innings")
monthlyhighFrame.grid(row=0, column=1, padx=10, pady=10)
monthLabel2 = Label(monthlyhighFrame, text="Month: ")
monthLabel2.grid(row=0, column=0, padx=10, pady=10)
highmonth = StringVar()
highmonthMenu = OptionMenu(monthlyhighFrame, highmonth, *months)
highmonthMenu.grid(row=0, column=1, padx=10, pady=10)
highmonthButton=Button(monthlyhighFrame, text="Show", command=showmonthhigh)
highmonthButton.grid(row=0, column=2, padx=10, pady=10)

monthlyhighfiveFrame=LabelFrame(reportsFrame, text="Players Top 5 Innings Average")
monthlyhighfiveFrame.grid(row=0, column=2, padx=10, pady=10)
monthLabel3 = Label(monthlyhighfiveFrame, text="Month: ")
monthLabel3.grid(row=0, column=0, padx=10, pady=10)
highfivemonth = StringVar()
highfivemonthMenu = OptionMenu(monthlyhighfiveFrame, highfivemonth, *months)
highfivemonthMenu.grid(row=0, column=1, padx=10, pady=10)
highfivemonthButton=Button(monthlyhighfiveFrame, text="Show", command=showmonthhighfive)
highfivemonthButton.grid(row=0, column=2, padx=10, pady=10)

clearreportButton=Button(reportsFrame, text="Clear Report", command=clearreport)
clearreportButton.grid(row=1, column=1, padx=10, pady=10)



quitButton=Button(root, text="Quit", command=root.quit, padx=100)
quitButton.grid(row=5, column=0, columnspan=4)

root.mainloop()
