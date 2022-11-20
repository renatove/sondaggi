import tkinter as tk
from tkinter import ttk
from MyDatabase import Connessione


class InputFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)
        self.combo_selected = 0
        self.__create_widgets()
        self.lista_lito = []
        self.lista_crono = []
        self.key = ""

    def __create_widgets(self):
        ttk.Label(self, text="Seleziona il pozzo").grid(column=0, row=0)
        self.combo_pozzi = ttk.Combobox(self)
        self.combo_pozzi['values'] = ('1','2','3','4')
        self.combo_pozzi.grid(column=1, row=0)
        self.combo_pozzi.bind("<<ComboboxSelected>>", self.callback)
        ttk.Button(self, text="Start", command=self.start).grid(column=0, row=1)
        ttk.Button(self, text="Save", command=self.save).grid(column=2, row=1)

    def callback(self, event):
        self.combo_selected = self.combo_pozzi.get()

    def save(self):
        print("Salva il risultato nel db")
        if len(self.lista_lito) == 0 or len(self.lista_crono) == 0:
            print("Dati non elaborati ...")
            return
        if len(self.lista_lito) != len(self.lista_crono):
            print("Errore sequenza stratigrafia...")
            return

        db = Connessione()

        # controllo sel il record è stato gia inserito
        sql = "select count(*) from stratigrafia where key = " + self.key + "group by key"
        db.query(sql)
        result = db.cur.fetchone()
        print(result)
        if result is not None:
            print("Il pozzo " + self.key + " è gia stato inserito ....")
            db.close()
            return

        try:
            for i in range(0, len(self.lista_lito)):
                l = self.lista_lito[i]
                c = self.lista_crono[i]
                print(l[0], l[1], l[2], l[3], c[4], c[5], l[4])
                sql = """INSERT INTO stratigrafia (key, ordine,  daprof, aprof, eta_sup, eta_inf, litologia)
                         VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                data = (str(l[0]), str(l[1]), str(l[2]), str(l[3]), c[4], c[5], l[4])
                db.query1(sql, data)
            db.conn.commit()
            db.cur.close()
            db.close()

            print("Il pozzo " + self.key + " è stato inserito ....")

        except Exception as e:
            print("Errore di inserimento dati ...")
            print(e)
            db.close()
            return

    def start(self):
        print(self.combo_selected)
        self.key = self.combo_selected
        cronostr = "pozzi_cronostr"
        litologia = "pozzi_litologia"

        # etrazione della sequnza strati combinando litologia e cronologia

        sql1 = "SELECT daprof FROM " + litologia + " WHERE key = " + str(self.key) + \
               "UNION " + \
               "SELECT daprof FROM " + cronostr + " WHERE key = " + str(self.key) + \
               "ORDER BY daprof"
        sql2 = "SELECT aprof FROM " + litologia + " WHERE key = " + str(self.key) + \
               "UNION " + \
               "SELECT aprof FROM " + cronostr + " WHERE key = " + str(self.key) + \
               "ORDER BY aprof"
        qstr1 = []
        qstr2 = []
        db = Connessione()
        db.query(sql1)
        daprof = db.cur.fetchall()
        for q in daprof:
            qstr1.append(q[0])
        db.query(sql2)
        aprof = db.cur.fetchall()
        for q in aprof:
            qstr2.append(q[0])

        # controllo se la lunghezza dei vettori è uguale

        if len(qstr1) != len(qstr2):
            print("Errore sequenza strati pozzo {0:8s}: {1:5d}, {2:5d}".format(self.key, len(qstr1), len(qstr2)))
            sql1 = "SELECT daprof FROM " + litologia + " WHERE key = " + str(self.key) + " ORDER BY daprof"
            sql2 = "SELECT aprof FROM " + litologia + " WHERE key = " + str(self.key) + " ORDER BY aprof"
            sql3 = "SELECT daprof FROM " + cronostr + " WHERE key = " + str(self.key) + " ORDER BY daprof"
            sql4 = "SELECT aprof FROM " + cronostr + " WHERE key = " + str(self.key) + " ORDER BY aprof"
            db.query(sql1)
            result = db.cur.fetchall()
            seq = []
            for q in result:
                seq.append(q[0])
            top1 = seq[0]
            db.query(sql2)
            result = db.cur.fetchall()
            seq = []
            for q in result:
                seq.append(q[0])
            end1 = seq[len(seq)-1]
            print('Litologia: Top {0:8.2f}  End {1:8.2f}'.format(top1, end1))
            db.query(sql3)
            result = db.cur.fetchall()
            seq = []
            for q in result:
                seq.append(q[0])
            top1 = seq[0]
            db.query(sql4)
            result = db.cur.fetchall()
            seq = []
            for q in result:
                seq.append(q[0])
            end1 = seq[len(seq)-1]
            print('Cronologia: Top {0:8.2f}  End {1:8.2f}'.format(top1, end1))
            db.close()
            return

        # stampa quote strati
        for i in range(0, len(qstr1)):
            print('{0:5d} {1:10.2f} {2:10.2f}'.format(i, qstr1[i], qstr2[i]))

        # elaborazione litologia

        sql1 = "SELECT daprof, aprof, litologia FROM " + litologia + " WHERE key = " + str(self.key)

        ordine = 1
        db.query(sql1)
        records = db.cur.fetchall()

        ns = 0
        self.lista_lito = []
        for rec in records:
            qt = rec[0]
            ql = rec[1]
            litol = rec[2]
            for i in range(ns, len(qstr1)):
                qls = qstr2[i]
                if qls <= ql:
                    print(self.key, ordine, qstr1[i], qstr2[i], litol)
                    self.lista_lito.append([self.key, ordine, qstr1[i], qstr2[i], litol])
                    ordine = ordine + 1
                else:
                    ns = i
                    break

        # eleaborazione cronostr

        sql1 = "SELECT daprof, aprof, eta_sup, eta_inf FROM " + cronostr + " WHERE key = " + str(self.key)
        ordine = 1
        db.query(sql1)
        records = db.cur.fetchall()
        start = records[0][0]
        skip = 0
        for i in range(0, len(qstr1)):
            if qstr1[i] == start:
                break
            skip = skip + 1
        print(start, skip)
        ns = skip
        self.lista_crono = []
        ordine = ordine + skip
        for rec in records:
            qt = rec[0]
            ql = rec[1]
            etasup = rec[2]
            etainf = rec[3]
            for i in range(ns, len(qstr1)):
                qls = qstr2[i]
                if qls <= ql:
                    print(self.key, ordine, qstr1[i], qstr2[i], etasup, etainf)
                    self.lista_crono.append([self.key, ordine, qstr1[i], qstr2[i], etasup, etainf])
                    ordine = ordine + 1
                else:
                    ns = i
                    break

        db.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Applicazione Sondaggi Profondi")
        self.eval('tk::PlaceWindow . center')
        self.geometry("400x200")
        self.resizable(0, 0)
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)

        self.__create_widgets()

    def __create_widgets(self):
        self.input_frame = InputFrame(self)
        self.input_frame.grid(column=1, row=1)

def carica_combo_pozzi(anagrafica):
    # Connect to an existing database
    db = Connessione()
    db.query("SELECT key FROM " + anagrafica)
    records = db.cur.fetchall()
    pozzi = list()
    for rec in records:
        key = rec[0]
        pozzi.append(key)
        app.input_frame.combo_pozzi['values'] = pozzi
    db.close()

## main program ##
anagrafica = "bdng__anagrafica"

app = App()

try:
    carica_combo_pozzi(anagrafica)



except Exception as e:
    print(e)

app.mainloop()
