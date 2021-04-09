def insert_import(original_body, addition):
    rtn = []
    state = 'on-top'
    for item in original_body:
        if state == 'on-top':
            if hasattr(item, 'body') and hasattr(item.body, '__iter__') and type(item.body[0]).__name__ in ['Import', 'ImportFrom', 'Expr']:
                pass
            else:
                state = 'in-position'

        if state == 'in-position':
            rtn.append(addition)  # TODO: if no other appends before, add newline after here
            state = 'on-bottom'
            
        rtn.append(item)
        
    return rtn
