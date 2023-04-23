import utils.constants, utils.encryption, utils.file

def create_file(file_name, file_content):
    # Use UUID for the file as we will be encrypting file name as well.
    file_id = utils.file.generate_file_id(file_name)
    file_path = utils.file.form_file_path(file_id)

    private_key, public_key = utils.encryption.create_rsa_key_pair()
    encrypted_file_name = utils.encryption.encrypt_data(public_key, file_name)
    encrypted_file_content = utils.encryption.encrypt_data(public_key, file_content)

    utils.constants.db_instance.save_new_file_info(file_id, file_path, encrypted_file_name, public_key, private_key)
    utils.file.store_file_to_fs(file_path, encrypted_file_content)

utils.constants.init_env()
create_file("file-1", "file_content")
