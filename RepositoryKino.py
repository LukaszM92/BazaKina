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
    def __init__(self, id, tytul=(), gatunek=(), dlugosc=(), seanse=[]):
        self.id = id
        self.tytul = tytul
        self.gatunek = gatunek
        self.dlugosc = dlugosc
        self.seanse = seanse



    def __repr__(self):
        return "<Filmy(id='%s', tytul='%s', items='%s')>" % (
                    self.id, self.tytul, self.seanse
                )


class SeanseItem():
    """Model występuje tylko wewnątrz obiektu Filmy.
    """
    def __init__(self, sala, dzien, godzina):
        self.sala = sala
        self.dzien = dzien
        self.godzina = godzina


    def __repr__(self):
        return "<SeanseItem(sala='%s', dzien='%s', godzina='%s')>" % (
                    self.sala, self.dzien, self.godzina
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

    def add(self, filmy):
        """Metoda dodaje pojedynczy film do bazy danych,
        wraz ze wszystkimi jego pozycjami
        """
        try:
            c = self.conn.cursor()

            c.execute('INSERT INTO Filmy (id, tytul, gatunek, dlugosc) VALUES(?, ?, ?, ?)',
                        (filmy.id, filmy.tytul, filmy.gatunek, filmy.dlugosc)
                    )
            # zapisz pozycje faktury
            if filmy.seanse:
                for seanseitem in filmy.seanse:
                    try:
                        c.execute('INSERT INTO Seanse (sala, dzien, godzina, filmy_id) VALUES(?,?,?,?)',
                                        (seanseitem.sala, seanseitem.dzien, seanseitem.godzina, filmy.id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding filmy item: %s, to filmy: %s' %
                                                    (str(seanseitem), str(filmy.id))
                                                )
        except Exception as e:
            #print "Filmy add error:", e
            raise RepositoryException('error adding filmy %s' % str(filmy))

    def delete(self, filmy):

        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Seanse WHERE filmy_id=?', (filmy.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Filmy WHERE id=?', (filmy.id,))

        except Exception as e:
            #print "Filmy delete error:", e
            raise RepositoryException('error deleting filmy %s' % str(filmy))

    def getById(self, id):
        """Get filmy by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Filmy WHERE id=?", (id,))
            seanse_row = c.fetchone()
            filmy = Filmy(id=id)
            if seanse_row == None:
                filmy=None
            else:
                filmy.sala = seanse_row[1]
                c.execute("SELECT * FROM Seanse WHERE filmy_id=? order by dzien", (id,))
                seanse_items_rows = c.fetchall()
                items_list = []
                for item_row in seanse_items_rows:
                    item = SeanseItem(sala=item_row[0], dzien=item_row[1], godzina=item_row[2])
                    items_list.append(item)
                filmy.seanse=items_list
        except Exception as e:
            #print "Filmy getById error:", e
            raise RepositoryException('error getting by id filmy_id: %s' % str(id))
        return filmy

    def update(self, filmy):
        """Metoda uaktualnia Filmy w bazie danych,
        wraz ze wszystkimi pozycjami.
        """
        try:
            # pobierz z bazy Filmy
            seanse_oryg = self.getById(filmy.id)
            if seanse_oryg != None:
                # Filmy jest w bazie: usuń ją
                self.delete(filmy)
            self.add(filmy)

        except Exception as e:
            #print "Filmy update error:", e
            raise RepositoryException('error updating filmy %s' % str(filmy))



if __name__ == '__main__':
    try:
        with FilmyRepository() as filmy_repository:
            filmy_repository.add(
                Filmy(id = 1, tytul='Szeregowiec Ryan', gatunek='Wojenne', dlugosc=1,
                        seanse = [
                            SeanseItem(sala = "Alfa",   dzien = '2017-02-16', godzina = '16:00:00'),
                            SeanseItem(sala = "Beta",   dzien = '2017-02-16', godzina = '20:00:00'),
                            SeanseItem(sala = "Gamma",  dzien = '2017-02-17', godzina = '16:00:00'),
                            SeanseItem(sala = "Delta",  dzien = '2017-02-17', godzina = '20:00:00'),
                            SeanseItem(sala = "Omega",  dzien = '2017-02-17', godzina = '22:00:00')
                        ]
                    )
                )
            filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(1)

if __name__ == '__main__':
    try:
        with FilmyRepository() as filmy_repository:
            filmy_repository.add(
                Filmy(id = 2, tytul='Titanic', gatunek='Melodramat', dlugosc=2,
                        seanse = [
                            SeanseItem(sala = "Alfa",   dzien = '2017-02-18', godzina = '15:00:00'),
                            SeanseItem(sala = "Beta",   dzien = '2017-02-18', godzina = '20:00:00'),
                            SeanseItem(sala = "Gamma",  dzien = '2017-02-19', godzina = '15:00:00'),
                            SeanseItem(sala = "Delta",  dzien = '2017-02-19', godzina = '20:00:00'),
                            SeanseItem(sala = "Omega",  dzien = '2017-02-19', godzina = '21:00:00')
                        ]
                    )
                )
            filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(2)

if __name__ == '__main__':
    try:
        with FilmyRepository() as filmy_repository:
            filmy_repository.add(
                Filmy(id = 3, tytul='Terminator', gatunek='Akcja', dlugosc=1.5,
                        seanse = [
                            SeanseItem(sala = "Alfa",   dzien = '2017-02-20', godzina = '17:00:00'),
                            SeanseItem(sala = "Beta",   dzien = '2017-02-20', godzina = '20:00:00'),
                            SeanseItem(sala = "Gamma",  dzien = '2017-02-21', godzina = '17:00:00'),
                            SeanseItem(sala = "Delta",  dzien = '2017-02-21', godzina = '20:00:00'),
                            SeanseItem(sala = "Omega",  dzien = '2017-02-21', godzina = '22:00:00')
                        ]
                    )
                )
            filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(3)

#### "UPDATE"
    try:
        with FilmyRepository() as filmy_repository:
            filmy_repository.update(
                Filmy(id = 1, tytul='Szeregowiec Ryan', gatunek='Wojenne',dlugosc=1,
                        seanse = [
                            SeanseItem(sala = "Alfa",   dzien = '2017-02-16', godzina = '16:30:00'),
                            SeanseItem(sala = "Beta",   dzien = '2017-02-16', godzina = '21:00:00'),
                            SeanseItem(sala = "Gamma",  dzien = '2017-02-17', godzina = '16:00:00'),
                            SeanseItem(sala = "Delta",  dzien = '2017-02-17', godzina = '20:00:00'),
                            SeanseItem(sala = "Omega",  dzien = '2017-02-18', godzina = '22:00:00')
                        ]
                    )
                )
            filmy_repository.complete()
    except RepositoryException as e:
        print(e)

    print FilmyRepository().getById(1)

#### "DELETE"

    try:
        with FilmyRepository() as filmy_repository:
            filmy_repository.delete( Filmy(id = 2) )
            filmy_repository.complete()
    except RepositoryException as e:
        print(e)
