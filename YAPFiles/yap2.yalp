/* Configuración del parser para Gramática No.2 */
/* Sigue la gramática SLR: */
/* E → E + T | E - T | T */
/* T → T ∗ F | T / F | F */
/* F → ( E ) | id | number */

%token ID
%token PLUS
%token MINUS
%token TIMES
%token DIV
%token NUMBER
%token LPAREN RPAREN
%token WHITESPACE
IGNORE WHITESPACE

%%

expression:
    expression PLUS term
  | expression MINUS term
  | term
;
term:
    term TIMES factor
  | term DIV factor
  | factor
;
factor:
    LPAREN expression RPAREN
  | ID
  | NUMBER
;