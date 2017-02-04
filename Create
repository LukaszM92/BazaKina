# -*- coding: utf-8 -*-

import sqlite3


db_path = 'Kino.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute("DROP TABLE IF EXISTS Filmy;")
c.execute('''
          CREATE TABLE IF NOT EXISTS Filmy
          ( id INTEGER PRIMARY KEY,
            tytul VARCHAR(100),
            gatunek VARCHAR(100),
            dlugosc NUMERIC NOT NULL
          )

          ''')
c.execute("DROP TABLE IF EXISTS Seanse;")
c.execute('''
          CREATE TABLE IF NOT EXISTS Seanse
          ( Sala VARCHAR(20),
            Dzien DATE NOT NULL,
            Godzina TIME NOT NULL,
            Filmy_id INTEGER,
            FOREIGN KEY(Filmy_id) REFERENCES Filmy(id),
            PRIMARY KEY (Sala, Filmy_id))
          ''')
