from django.db.backends import BaseDatabaseIntrospection
import pyodbc as Database

SQL_AUTOFIELD = -777555

class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Map type codes to Django Field types.
    data_types_reverse = {
        SQL_AUTOFIELD:                  'AutoField',
        Database.SQL_BIGINT:            'IntegerField',
        #Database.SQL_BINARY:            ,
        Database.SQL_BIT:               'BooleanField',
        Database.SQL_CHAR:              'CharField',
        Database.SQL_DECIMAL:           'DecimalField',
        Database.SQL_DOUBLE:            'FloatField',
        Database.SQL_FLOAT:             'FloatField',
        Database.SQL_GUID:              'TextField',
        Database.SQL_INTEGER:           'IntegerField',
        #Database.SQL_LONGVARBINARY:     ,
        #Database.SQL_LONGVARCHAR:       ,
        Database.SQL_NUMERIC:           'DecimalField',
        Database.SQL_REAL:              'FloatField',
        Database.SQL_SMALLINT:          'SmallIntegerField',
        Database.SQL_TINYINT:           'SmallIntegerField',
        Database.SQL_TYPE_DATE:         'DateField',
        Database.SQL_TYPE_TIME:         'TimeField',
        Database.SQL_TYPE_TIMESTAMP:    'DateTimeField',
        #Database.SQL_VARBINARY:         ,
        Database.SQL_VARCHAR:           'TextField',
        Database.SQL_WCHAR:             'CharField',
        Database.SQL_WLONGVARCHAR:      'TextField',
        Database.SQL_WVARCHAR:          'TextField',
    }

    def get_table_list(self, cursor):
        """
        Returns a list of table names in the current database.
        """
#        db = cursor.db.alias
#        if db == 'default':
        db = 'public'
        cursor.execute("SELECT TABLE_NAME FROM V_CATALOG.TABLES WHERE is_system_table = 'f' and table_schema = '%s'" % db)
        return [row[0] for row in cursor.fetchall()]


    def get_table_description(self, cursor, table_name, identity_check=True):
        "Returns a description of the table, with the DB-API cursor.description interface."
        cursor.execute("SELECT * FROM %s LIMIT 1" % self.connection.ops.quote_name(table_name))
        return cursor.description

    def _name_to_index(self, cursor, table_name):
        """
        Returns a dictionary of {field_name: field_index} for the given table.
        Indexes are 0-based.
        """
        return dict([(d[0], i) for i, d in enumerate(self.get_table_description(cursor, table_name, identity_check=False))])

    def get_relations(self, cursor, table_name):
        """
        Returns a dictionary of {field_index: (field_index_other_table, other_table)}
        representing all relationships to the given table. Indexes are 0-based.
        """
        cursor.execute("""
SELECT fk.ORDINAL_POSITION, col.ORDINAL_POSITION, fk.REFERENCE_TABLE_NAME
FROM FOREIGN_KEYS fk
INNER JOIN COLUMNS col on fk.REFERENCE_COLUMN_NAME = col.COLUMN_NAME
                       and fk.REFERENCE_TABLE_NAME = col.TABLE_NAME
WHERE fk.TABLE_NAME = %s
""", [table_name])
        relations = {}
        for row in cursor.fetchall():
            # row[0] and row[1] are like "{2}", so strip the curly braces.
            relations[int(row[0].strip()) - 1] = (int(row[1].strip()) - 1, row[2])
        return relations

    def get_indexes(self, cursor, table_name):
        """
        Returns a dictionary of fieldname -> infodict for the given table,
        where each infodict is in the format:
            {'primary_key': boolean representing whether it's the primary key,
             'unique': boolean representing whether it's a unique index,
             'db_index': boolean representing whether it's a non-unique index}
        """
        cursor.execute("""
SELECT col.COLUMN_NAME, pk.CONSTRAINT_TYPE
FROM PRIMARY_KEYS pk
right join COLUMNS col on pk.COLUMN_NAME = col.COLUMN_NAME
                        and pk.TABLE_NAME = col.TABLE_NAME
WHERE fk.TABLE_NAME = %s
""", [table_name])
        indexes = {}
        for row in cursor.fetchall():
            indexes[row[0]] = {'primary_key': row[1] == 'p', 'unique': True}
        return indexes

