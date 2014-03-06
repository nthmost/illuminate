import time, os

def select_file_from_aliases(codename, filemap, basepath):
    "acquires first physical file available in dataset matching codename."
    #assume that list in filemap has first item as most likely file.
    for item in filemap[codename]:
        filepath = os.path.join(basepath, item)
        if os.path.exists(filepath):
            return filepath
    # none of the possible files extant
    return None

def set_column_sequence(dataframe, seq):
    '''
    Returns pandas DataFrame with the columns named in seq as first columns.
    
    :param dataframe: pandas DataFrame to be resorted according to seq.
    :param seq: array of column names.
    '''
    # http://stackoverflow.com/questions/12329853/how-to-rearrange-pandas-column-sequence
    cols = seq[:] # copy so we don't mutate seq
    for x in dataframe.columns:
        if x not in cols:
            cols.append(x)
    return dataframe[cols]
    
