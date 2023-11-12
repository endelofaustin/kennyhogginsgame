import py2exe

if __name__ == '__main__':
    py2exe.freeze(
        windows=[{
            'script': './main.py',
            'dest_base': './kenny1'
        }],
        options={
            'verbose': 4
        }
    )
