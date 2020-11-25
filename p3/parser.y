%{
	#include <stdio.h>
	#include <stdlib.h>
	extern int yylex();
	extern char* yytext;
	extern FILE* yyin;
%}

%start start
%token RENAME ATTRIBUTE WHERE LBRACE RBRACE LPAREN RPAREN COMMA UNION INTERSECT MINUS TIMES JOIN DIVIDEBY LT GT LEQ GEQ EQ NEQ CNO CITY CNAME SNO PNO TQTY SNAME QUOTA PNAME COST AVQTY SPOUND STATUS PPOUND COLOR WEIGHT QTY S P SP PRDCT CUST ORDERS number AS ERROR

%%
start: expression

expression: one_relation_expression | two_relation_expression

one_relation_expression: renaming | restriction | projection

renaming: term RENAME attribute AS attribute

term: relation | LPAREN expression RPAREN

restriction: term WHERE comparison

projection: term | term LBRACE attribute_commalist RBRACE

attribute_commalist: attribute | attribute COMMA attribute_commalist

two_relation_expression: projection binary_operation expression

binary_operation: UNION | INTERSECT | MINUS | TIMES | JOIN | DIVIDEBY

comparison: attribute compare number

compare: LT | GT | LEQ | GEQ | EQ | NEQ

attribute: CNO | CITY | CNAME | SNO | PNO | TQTY |
		  SNAME | QUOTA | PNAME | COST | AVQTY |
		  SPOUND | STATUS | PPOUND | COLOR | WEIGHT | QTY

relation: S | P | SP | PRDCT | CUST | ORDERS
%%

int yyerror(char* s) {
	puts("REJECT");
	exit(0);
}

int yywrap() {
	return 1;
}

int main(int argc, char** argv) {
	if (argc > 0) {
		yyin = fopen(argv[1], "r");
		if (!yyin) {
			puts("bad test case");
			exit(0);
		}
	}

	yyparse();
	puts("ACCEPT");
	return 0;
}
