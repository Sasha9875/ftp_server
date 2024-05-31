import os
import shutil
import socket

WORKING_DIR = r'.\user'

current_dir = WORKING_DIR  # Переменная для отслеживания текущей директории

def process(req):
    global current_dir
    command = req.split()
    
    if not command:
        return 'bad request'
    
    if command[0] == 'ls':
        return '; '.join(os.listdir(current_dir))
    
    elif command[0] == 'pwd':
        return current_dir
    
    elif command[0] == 'cd':
        if len(command) < 2:
            return 'bad request: missing folder name'
        new_dir = os.path.join(current_dir, command[1])
        if os.path.isdir(new_dir):
            current_dir = new_dir
            return f"Changed directory to {new_dir}"
        else:
            return f"Directory {command[1]} does not exist"
    
    elif command[0] == 'mkdir':
        if len(command) < 2:
            return 'bad request: missing folder name'
        folder_path = os.path.join(current_dir, command[1])
        try:
            os.makedirs(folder_path, exist_ok=True)
            return f"Directory {command[1]} created"
        except Exception as e:
            return f"Error creating directory {command[1]}: {e}"
    
    elif command[0] == 'rmdir':
        if len(command) < 2:
            return 'bad request: missing folder name'
        folder_path = os.path.join(current_dir, command[1])
        try:
            shutil.rmtree(folder_path)
            return f"Directory {command[1]} removed"
        except Exception as e:
            return f"Error removing directory {command[1]}: {e}"
    
    elif command[0] == 'rm':
        if len(command) < 2:
            return 'bad request: missing file name'
        file_path = os.path.join(current_dir, command[1])
        try:
            os.remove(file_path)
            return f"File {command[1]} removed"
        except Exception as e:
            return f"Error removing file {command[1]}: {e}"
    
    elif command[0] == 'mv':
        if len(command) < 3:
            return 'bad request: missing source or destination'
        src_path = os.path.join(current_dir, command[1])
        dst_path = os.path.join(current_dir, command[2])
        try:
            shutil.move(src_path, dst_path)
            return f"Moved {command[1]} to {command[2]}"
        except Exception as e:
            return f"Error moving {command[1]} to {command[2]}: {e}"
    
    elif command[0] == 'upload':
        if len(command) < 3:
            return 'bad request: missing file name or content'
        file_path = os.path.join(current_dir, command[1])
        try:
            with open(file_path, 'w') as f:
                f.write(' '.join(command[2:]))
            return f"File {command[1]} uploaded"
        except Exception as e:
            return f"Error uploading file {command[1]}: {e}"
    
    elif command[0] == 'download':
        if len(command) < 2:
            return 'bad request: missing file name'
        file_path = os.path.join(current_dir, command[1])
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error downloading file {command[1]}: {e}"
    
    elif command[0] == 'exit':
        return 'exit'
    
    else:
        return 'bad request'

def start_server():
    PORT = 9090
    sock = socket.socket()
    sock.bind(('', PORT))
    sock.listen()
    
    print("Listening on port", PORT)
    while True:
        conn, addr = sock.accept()
        print("Connection from", addr)
        
        request = conn.recv(1024).decode()
        print("Request:", request)
        
        response = process(request)
        if response == 'exit':
            conn.close()
            break
        conn.send(response.encode())
        
        conn.close()
    sock.close()

if __name__ == "__main__":
    start_server()
