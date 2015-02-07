CREATE SCHEMA partitions
  AUTHORIZATION zabbix;
  
  -- Function: trg_partition()
 
-- DROP FUNCTION trg_partition();
 
CREATE OR REPLACE FUNCTION trg_partition()
  RETURNS TRIGGER AS
$BODY$
DECLARE
prefix text := 'partitions.';
timeformat text;
selector text;
_interval INTERVAL;
tablename text;
startdate text;
enddate text;
create_table_part text;
create_index_part text;
BEGIN
 
selector = TG_ARGV[0];
 
IF selector = 'day' THEN
timeformat := 'YYYY_MM_DD';
ELSIF selector = 'month' THEN
timeformat := 'YYYY_MM';
END IF;
 
_interval := '1 ' || selector;
tablename :=  TG_TABLE_NAME || '_p' || TO_CHAR(TO_TIMESTAMP(NEW.clock), timeformat);
 
EXECUTE 'INSERT INTO ' || prefix || quote_ident(tablename) || ' SELECT ($1).*' USING NEW;
RETURN NULL;
 
EXCEPTION
WHEN undefined_table THEN
 
startdate := EXTRACT(epoch FROM date_trunc(selector, TO_TIMESTAMP(NEW.clock)));
enddate := EXTRACT(epoch FROM date_trunc(selector, TO_TIMESTAMP(NEW.clock) + _interval ));
 
create_table_part:= 'CREATE TABLE IF NOT EXISTS '|| prefix || quote_ident(tablename) || ' (CHECK ((clock >= ' || quote_literal(startdate) || ' AND clock < ' || quote_literal(enddate) || '))) INHERITS ('|| TG_TABLE_NAME || ')';
create_index_part:= 'CREATE INDEX '|| quote_ident(tablename) || '_1 on ' || prefix || quote_ident(tablename) || '(itemid,clock)';
 
EXECUTE create_table_part;
EXECUTE create_index_part;
 
--insert it again
EXECUTE 'INSERT INTO ' || prefix || quote_ident(tablename) || ' SELECT ($1).*' USING NEW;
RETURN NULL;
 
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trg_partition()
  OWNER TO postgres;
Create a trigger for each (clock based) table you want to partition
CREATE TRIGGER partition_trg BEFORE INSERT ON history           FOR EACH ROW EXECUTE PROCEDURE trg_partition('day');
CREATE TRIGGER partition_trg BEFORE INSERT ON history_sync      FOR EACH ROW EXECUTE PROCEDURE trg_partition('day');
CREATE TRIGGER partition_trg BEFORE INSERT ON history_uint      FOR EACH ROW EXECUTE PROCEDURE trg_partition('day');
CREATE TRIGGER partition_trg BEFORE INSERT ON history_str_sync  FOR EACH ROW EXECUTE PROCEDURE trg_partition('day');
CREATE TRIGGER partition_trg BEFORE INSERT ON history_log       FOR EACH ROW EXECUTE PROCEDURE trg_partition('day');
CREATE TRIGGER partition_trg BEFORE INSERT ON trends            FOR EACH ROW EXECUTE PROCEDURE trg_partition('month');
CREATE TRIGGER partition_trg BEFORE INSERT ON trends_uint       FOR EACH ROW EXECUTE PROCEDURE trg_partition('month');


DROP TRIGGER partition_trg ON history;
DROP TRIGGER partition_trg ON history_sync;
DROP TRIGGER partition_trg ON history_uint;
DROP TRIGGER partition_trg ON history_str_sync;
DROP TRIGGER partition_trg ON history_log;
DROP TRIGGER partition_trg ON trends;
DROP TRIGGER partition_trg ON trends_uint;


-- Function: delete_partitions(interval, text)
 
-- DROP FUNCTION delete_partitions(interval, text);
 
CREATE OR REPLACE FUNCTION delete_partitions(intervaltodelete INTERVAL, tabletype text)
  RETURNS text AS
$BODY$
DECLARE
result RECORD ;
prefix text := 'partitions.';
table_timestamp TIMESTAMP;
delete_before_date DATE;
tablename text;
 
BEGIN
    FOR result IN SELECT * FROM pg_tables WHERE schemaname = 'partitions' LOOP
 
        table_timestamp := TO_TIMESTAMP(substring(result.tablename FROM '[0-9_]*$'), 'YYYY_MM_DD');
        delete_before_date := date_trunc('day', NOW() - intervalToDelete);
        tablename := result.tablename;
 
    -- Was it called properly?
        IF tabletype != 'month' AND tabletype != 'day' THEN
	    RAISE EXCEPTION 'Please specify "month" or "day" instead of %', tabletype;
        END IF;
 
 
    --Check whether the table name has a day (YYYY_MM_DD) or month (YYYY_MM) format
        IF LENGTH(substring(result.tablename FROM '[0-9_]*$')) = 10 AND tabletype = 'month' THEN
            --This is a daily partition YYYY_MM_DD
            -- RAISE NOTICE 'Skipping table % when trying to delete "%" partitions (%)', result.tablename, tabletype, length(substring(result.tablename from '[0-9_]*$'));
            CONTINUE;
        ELSIF LENGTH(substring(result.tablename FROM '[0-9_]*$')) = 7 AND tabletype = 'day' THEN
            --this is a monthly partition
            --RAISE NOTICE 'Skipping table % when trying to delete "%" partitions (%)', result.tablename, tabletype, length(substring(result.tablename from '[0-9_]*$'));
            CONTINUE;
        ELSE
            --This is the correct table type. Go ahead and check if it needs to be deleted
	    --RAISE NOTICE 'Checking table %', result.tablename;
        END IF;
 
	IF table_timestamp <= delete_before_date THEN
		RAISE NOTICE 'Deleting table %', quote_ident(tablename);
		EXECUTE 'DROP TABLE ' || prefix || quote_ident(tablename) || ';';
	END IF;
    END LOOP;
RETURN 'OK';
 
END;
 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION delete_partitions(INTERVAL, text)
  OWNER TO postgres;
  
  