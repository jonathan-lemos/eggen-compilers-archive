all:
	bison -d parser.y
	lex lex.l
	gcc -o parser lex.yy.c parser.tab.c

clean:
	rm -f parser *.c *.h
