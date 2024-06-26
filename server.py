import os
import shutil
import socket
import logging

WORKING_DIR = '/path/to/working/directory'  # Укажите путь к рабочей директории

# Настройка логирования
logging.basicConfig(level=logging.INFO)
connection_logger = logging.getLogger('connection')
authorization_logger = logging.getLogger('authorization')
file_operations_logger = logging.getLogger('file_operations')

connection_handler = logging.FileHandler('connections.log')
authorization_handler = logging.FileHandler('authorization.log')
file_operations_handler = logging.FileHandler('file_operations.log')

connection_logger.addHandler(connection_handler)
authorization_logger.addHandler(authorization_handler)
file_operations_logger.addHandler(file_operations_handler)

current_dir = WORKING_DIR  # Переменная для отслеживания текущей директории

def is_within_working_dir(path):
    abs_working_dir = os.path.abspath(WORKING_DIR)
    abs_path = os.path.abspath(path)
    return os.path.commonpath([abs_working_dir]) == os.path.commonpath([abs_working_dir, abs_path])

def process(req):
    global current_dir
    command = req.split()
    
    if not command:
        return 'bad request'
    
    if command[0] == 'ls':
        result = '; '.join(os.listdir(current_dir))
        file_operations_logger.info(f"Listed directory: {current_dir}")
        return result
    
    elif command[0] == 'pwd':
        file_operations_logger.info(f"Requested current directory: {current_dir}")
        return current_dir
    
    elif command[0] == 'cd':
        if len(command) < 2:
            return 'bad request: missing folder name'
        if command[1] == '..':
            new_dir = os.path.dirname(current_dir)
            if is_within_working_dir(new_dir):
                current_dir = new_dir
                file_operations_logger.info(f"Changed directory to: {new_dir}")
                return f"Changed directory to {new_dir}"
            else:
                return "Cannot move above the working directory"
        elif command[1] == '/':
            current_dir = WORKING_DIR
            file_operations_logger.info(f"Changed directory to root: {WORKING_DIR}")
            return f"Changed directory to {WORKING_DIR}"
        else:
            new_dir = os.path.join(current_dir, command[1])
            if os.path.isdir(new_dir) and is_within_working_dir(new_dir):
                current_dir = new_dir
                file_operations_logger.info(f"Changed directory to: {new_dir}")
                return f"Changed directory to {new_dir}"
            else:
                return f"Directory {command[1]} does not exist or is out of bounds"
    
    elif command[0] == 'mkdir':
        if len(command) < 2:
            return 'bad request: missing folder name'
        folder_path = os.path.join(current_dir, command[1])
        if is_within_working_dir(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                file_operations_logger.info(f"Created directory: {folder_path}")
                return f"Directory {command[1]} created"
            except Exception as e:
                return f"Error creating directory {command[1]}: {e}"
        else:
            return 'bad request: out of bounds'
    
    elif command[0] == 'rmdir':
        if len(command) < 2:
            return 'bad request: missing folder name'
        folder_path = os.path.join(current_dir, command[1])
        if is_within_working_dir(folder_path):
            try:
                shutil.rmtree(folder_path)
                file_operations_logger.info(f"Removed directory: {folder_path}")
                return f"Directory {command[1]} removed"
            except Exception as e:
                return f"Error removing directory {command[1]}: {e}"
        else:
            return 'bad request: out of bounds'
    
    elif command[0] == 'rm':
        if len(command) < 2:
            return 'bad request: missing file name'
        file_path = os.path.join(current_dir, command[1])
        if is_within_working_dir(file_path):
            try:
                os.remove(file_path)
                file_operations_logger.info(f"Removed file: {file_path}")
                return f"File {command[1]} removed"
            except Exception as e:
                return f"Error removing file {command[1]}: {e}"
        else:
            return 'bad request: out of bounds'
    
    elif command[0] == 'mv':
        if len(command) < 3:
            return 'bad request: missing source or destination'
        src_path = os.path.join(current_dir, command[1])
        dst_path = os.path.join(current_dir, command[2])
        if is_within_working_dir(src_path) and is_within_working_dir(dst_path):
            try:
                shutil.move(src_path, dst_path)
                file_operations_logger.info(f"Moved {src_path} to {dst_path}")
                return f"Moved {command[1]} to {command[2]}"
            except Exception as e:
                return f"Error moving {command[1]} to {command[2]}: {e}"
        else:
            return 'bad request: out of bounds'
    
    elif command[0] == 'upload':
        if len(command) < 3:
            return 'bad request: missing file name or content'
        file_path = os.path.join(current_dir, command[1])
        if is_within_working_dir(file_path):
            try:
                with open(file_path, 'w') as f:
                    f.write(' '.join(command[2:]))
                file_operations_logger.info(f"Uploaded file: {file_path}")
                return f"File {command[1]} uploaded"
            except Exception as e:
                return f"Error uploading file {command[1]}: {e}"
        else:
            return 'bad request: out of bounds'
    
    elif command[0] == 'download':
        if len(command) < 2:
            return 'bad request: missing file name'
        file_path = os.path.join(current_dir, command[1])
        if is_within_working_dir(file_path):
            try:
                with open(file_path, 'r') as f:
                    file_operations_logger.info(f"Downloaded file: {file_path}")
                    return f.read()
            except Exception as e:
                return f"Error downloading file {command[1]}: {e}"
        else:
            return 'bad request: out of bounds'
    
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
        connection_logger.info(f"Connection from {addr}")
        
        request = conn.recv(1024).decode()
        connection_logger.info(f"Request: {request}")
        
        response = process(request)
        if response == 'exit':
            conn.close()
            break
        conn.send(response.encode())
        
        conn.close()
    sock.close()

if __name__ == "__main__":
    start_server()
