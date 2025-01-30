import pymysql 

conn = pymysql.connect(user = "root",password = "root",database="pfms_db",host="localhost",port=3306)
cur = conn.cursor()

# exp_trans = 'select * from transactionmodel where transaction_type = "Expenses"'
# cur.execute(exp_trans)
# data_exp = cur.fetchall()
# column_names = [desc[0] for desc in cur.description]

# data_as_dict = [tuple(zip(column_names, row)) for row in data_exp]
# print(data)


# for query in data_exp:
#         q = list(query)
#         del q[7]
#         db_query = "INSERT INTO expensemodel VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#         cur.execute(db_query, tuple(q))
#         conn.commit()
#         print(db_query)
#         Done



# income_trans = 'select * from transactionmodel where transaction_type = "Income"'
# cur.execute(income_trans)
# data_income = cur.fetchall()

# for query in data_income:
#     q = list(query)
#     del q[7]
#     db_query = "INSERT INTO incomemodel VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#     cur.execute(db_query, tuple(q))
#     conn.commit()
#     print(db_query)
       



