import utils.constants
import utils.encryption
import utils.file


def create_file(file_name, file_content):
    # Use UUID for the file as we will be encrypting file name as well.
    file_id = utils.file.generate_file_id(file_name)
    file_path = utils.file.form_file_path(file_id)
    owner = utils.constants.ip_addr

    private_key, public_key = utils.encryption.create_rsa_key_pair()
    en_file_name = utils.encryption.encrypt_data(public_key, file_name)
    encrypted_file_content = utils.encryption.encrypt_data(
        public_key, file_content)

    utils.constants.db_instance.save_new_file_info(
        file_id, file_path, en_file_name, owner, public_key, private_key)
    utils.file.store_file_to_fs(file_path, encrypted_file_content)

    return file_id


def read_encrypted_file(file_id):
    file_details = utils.constants.db_instance.get_file_details(file_id)

    encrypted_data = utils.file.read_file(file_details['file_path'])
    decrypted_data = utils.encryption.decrypt_data(
        file_details['private_key'], encrypted_data)

    return decrypted_data


def get_accessible_files():
    owned_files = utils.constants.db_instance.get_owned_files()
    shared_files = utils.constants.db_instance.get_shared_files()

    accessible_files = []
    for file in owned_files:
        accessible_files.append({
            'file_id': file,
            'permission_write': 1
        })

    if len(shared_files) != 0:
        accessible_files.append(shared_files)

    return accessible_files
