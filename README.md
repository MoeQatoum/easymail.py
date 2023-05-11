# EasyMail
Automate sending emails. EasyMail creates `timestamp.json` and stores a timestamp to each e-mail account to avoid spamming. Get your email settings from [here](https://emailsettings.email)

## Usage:
- **Sending emails to contacts list from files**:
```console
$ ./easymail sample_emails_file.txt
$ ./easymail sample_emails_file_1.txt,sample_emails_file_2.txt
```

- **Sending emails to manually entered email accounts directly**: 
```console
$ ./easymail email_account_1@gmail.com
$ ./easymail email_account_1@gmail.com,email_account_2@hotmail.com.com
```

use ```--help``` flag for all options.
