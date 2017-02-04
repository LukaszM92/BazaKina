# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

#
# Ścieżka połączenia z bazą danych
#
db_path = 'Kino.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


#
# Model danych
#
class Filmy():
    """
    """
    def __init__(self, id, tytul=(), gatunek=(), dlugosc=(), Seanse=[]):
        self.id = id
        self.tytul = tytul
        self.gatunek = gatunek
        self.dlugosc = dlugosc
        self.Seanse = Seanse



    def __repr__(self):
        return "<Filmy(id='%s', tytul='%s', items='%s')>" % (
                    self.id, self.tytul, self.Seanse
                )


class SeanseItem():
    """Model występuje tylko wewnątrz obiektu Filmy.
    """
    def __init__(self, Sala, Dzien, Godzina):
        self.Sala = Sala
        self.Dzien = Dzien
        self.Godzina = Godzina


    def __repr__(self):
        return "<SeanseItem(Sala='%s', Dzien='%s', Godzina='%s')>" % (
                    self.Sala, self.Dzien, self.Godzina
                )


#
# Klasa bazowa repozytorium
#
class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow typu Ksiazka
#
class FilmyRepository(Repository):

    def add(self, Filmy):
        """Metoda dodaje pojedynczy film do bazy danych,
        wraz ze wszystkimi jego pozycjami
        """
        try:
            c = self.conn.cursor()

            c.execute('INSERT INTO Filmy (id, tytul, gatunek, dlugosc) VALUES(?, ?, ?, ?)',
                        (Filmy.id, Filmy.tytul, Filmy.gatunek, filmy.dlugosc)
                    )
            # zapisz pozycje faktury
            if filmy.Seanse:
                for Seanseitem in filmy.Seanse:
                    try:
                        c.execute('INSERT INTO Seanse (Sala, Dzien, Godzina, Filmy_id) VALUES(?,?,?,?)',
                                        (Seanseitem.Sala, Seanseitem.Dzien, Seanseitem.Godzina, Filmy_id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding Filmy item: %s, to Filmy: %s' %
                                                    (str(Seanseitem), str(Filmy.id))
                                                )
        except Exception as e:
            #print "Filmy add error:", e
            raise RepositoryException('error adding Filmy %s' % str(Filmy))

    def delete(self, Filmy):

        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Seanse WHERE Filmy_id=?', (Filmy.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Filmy WHERE id=?', (Filmy.id,))

        except Exception as e:
            #print "Filmy delete error:", e
            raise RepositoryException('error deleting Filmy %s' % str(Filmy))

    def getById(self, id):
        """Get Filmy by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Filmy WHERE id=?", (id,))
            Seanse_row = c.fetchone()
            Filmy = Filmy(id=id)
            if Seanse_row == None:
                Filmy=None
            else:
                Filmy.Sala = Seanse_row[1]
                c.execute("SELECT * FROM Seanse WHERE Filmy_id=? order by Dzien", (id,))
                Seanse_items_rows = c.fetchall()
                items_list = []
                for item_row in Seanse_items_rows:
                    item = SeanseItem(Sala=item_row[0], Dzien=item_row[1], Godzina=item_row[2])
                    items_list.append(item)
                Filmy.Seanse=items_list
        except Exception as e:
            #print "Filmy getById error:", e
            raise RepositoryException('error getting by id Filmy_id: %s' % str(id))
        return Filmy

    def update(self, Filmy):
        """Metoda uaktualnia Filmy w bazie danych,
        wraz ze wszystkimi pozycjami.
        """
        try:
            # pobierz z bazy Filmy
            Seanse_oryg = self.getById(Filmy.id)
            if Seanse_oryg != None:
                # Filmy jest w bazie: usuń ją
                self.delete(Filmy)
            self.add(Filmy)

        except Exception as e:
            #print "Filmy update error:", e
            raise RepositoryException('error updating Filmy %s' % str(Filmy))



if __name__ == '__main__':
    try:
        with FilmyRepository() as Filmy_repository:
            Filmy_repository.add(
                Filmy(id = 1, tytul='Szeregowiec Ryan', gatunek='Wojenne',
                        Seanse = [
                            SeanseItem(Sala = "Alfa",   Dzien = '2017-02-16', Godzina = '16:00:00'),
                            SeanseItem(Sala = "Beta",   Dzien = '2017-02-16', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Gamma",  Dzien = '2017-02-17', Godzina = '16:00:00'),
                            SeanseItem(Sala = "Delta",  Dzien = '2017-02-17', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Omega",  Dzien = '2017-02-17', Godzina = '22:00:00')
                        ]
                    )
                )
            Filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(1)

if __name__ == '__main__':
    try:
        with FilmyRepository() as Filmy_repository:
            Filmy_repository.add(
                Filmy(id = 2, tytul='Titanic', gatunek='Melodramat',
                        Seanse = [
                            SeanseItem(Sala = "Alfa",   Dzien = '2017-02-18', Godzina = '15:00:00'),
                            SeanseItem(Sala = "Beta",   Dzien = '2017-02-18', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Gamma",  Dzien = '2017-02-19', Godzina = '15:00:00'),
                            SeanseItem(Sala = "Delta",  Dzien = '2017-02-19', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Omega",  Dzien = '2017-02-19', Godzina = '21:00:00')
                        ]
                    )
                )
            Filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(2)

if __name__ == '__main__':
    try:
        with FilmyRepository() as Filmy_repository:
            Filmy_repository.add(
                Filmy(id = 3, tytul='Terminator', gatunek='Akcja',
                        Seanse = [
                            SeanseItem(Sala = "Alfa",   Dzien = '2017-02-20', Godzina = '17:00:00'),
                            SeanseItem(Sala = "Beta",   Dzien = '2017-02-20', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Gamma",  Dzien = '2017-02-21', Godzina = '17:00:00'),
                            SeanseItem(Sala = "Delta",  Dzien = '2017-02-21', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Omega",  Dzien = '2017-02-21', Godzina = '22:00:00')
                        ]
                    )
                )
            Filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(3)


    try:
        with FilmyRepository() as FilmyRepository_repository:
            Filmy_repository.update(
                Filmy(id = 1, tytul='Szeregowiec Ryan', gatunek='Wojenne',
                        Seanse = [
                            SeanseItem(Sala = "Alfa",   Dzien = '2017-02-16', Godzina = '16:30:00'),
                            SeanseItem(Sala = "Beta",   Dzien = '2017-02-16', Godzina = '21:00:00'),
                            SeanseItem(Sala = "Gamma",   Dzien = '2017-02-17', Godzina = '16:00:00'),
                            SeanseItem(Sala = "Delta",   Dzien = '2017-02-17', Godzina = '20:00:00'),
                            SeanseItem(Sala = "Omega",   nDzien = '2017-02-18', Godzina = '22:00:00')
                        ]
                    )
                )
            Filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(1)



    try:
        with FilmyRepository() as Filmy_repository:
            Filmy_repository.delete( Filmy(id = 2) )
            Filmy_repository.complete()
    except RepositoryException as e:
        print(e)
