%{
	#include "parser.tab.h"
	extern int yylval;
%}
whitespace [ \t\n]+
number [0-9]+
any .
%%
{whitespace} ;
{number}  return(number);
"AS"  return(AS);
"RENAME"  return(RENAME);
"ATTRIBUTE"  return(ATTRIBUTE);
"WHERE"  return(WHERE);
"["  return(LBRACE);
"]"  return(RBRACE);
"("  return(LPAREN);
")"  return(RPAREN);
","  return(COMMA);
"UNION"  return(UNION);
"INTERSECT"  return(INTERSECT);
"MINUS"  return(MINUS);
"TIMES"  return(TIMES);
"JOIN"  return(JOIN);
"DIVIDEBY"  return(DIVIDEBY);
"<"  return(LT);
">"  return(GT);
"<="  return(LEQ);
">="  return(GEQ);
"="  return(EQ);
"<>"  return(NEQ);
"CNO"  return(CNO);
"CITY"  return(CITY);
"CNAME"  return(CNAME);
"SNO"  return(SNO);
"PNO"  return(PNO);
"TQTY"  return(TQTY);
"SNAME"  return(SNAME);
"QUOTA"  return(QUOTA);
"PNAME"  return(PNAME);
"COST"  return(COST);
"AVQTY"  return(AVQTY);
"S#"  return(SPOUND);
"STATUS"  return(STATUS);
"P#"  return(PPOUND);
"COLOR"  return(COLOR);
"WEIGHT"  return(WEIGHT);
"QTY"  return(QTY);
"S"  return(S);
"P"  return(P);
"SP"  return(SP);
"PRDCT"  return(PRDCT);
"CUST"  return(CUST);
"ORDERS"  return(ORDERS);
{any}  return(ERROR);
%%
