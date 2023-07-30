import argparse 
from easymail import *

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    settings_args = parser.add_argument_group(title="Easy Mail settings options")
    email_msg_args = parser.add_argument_group(title="Email Message options")
    contact_selection_args = parser.add_argument_group(title="Contacts selection options")
    parser.add_argument(
        "mailList",
        help="Mail list, email accounts or list of files containing email accounts, separated by ','",
    )
    email_msg_args.add_argument(
        "-s",
        "--subject",
        default=None,
        help="Email message subject."
    )
    email_msg_args.add_argument(
        "-b",
        "--body",
        default=None,
        help="Email message body path, can be string, HTML file, or TXT file.",
    )
    email_msg_args.add_argument(
        "-a",
        "--attachment-path",
        default=None,
        help="Attachment path. Defaults to path specified in config.json, [PDF, DOCX, DOC].",
    )
    contact_selection_args.add_argument(
        "-r",
        "--range",
        default=None,
        help='Specify a range of emails from a file or list of files. FORMAT: "START<INT>-END<INT>".',
    )
    settings_args.add_argument(
        "-cfg",
        "--config_file_path",
        default=None,
        action="store_true",
        help="Override frequent sending protection.",
    )
    settings_args.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Override frequent sending protection.",
    )
    settings_args.add_argument(
        "-d",
        "--delivery-report",
        default=False,
        action="store_true",
        help="enable delivery report.",
    )
    email_msg_args.add_argument(
        "-bf",
        "--body-format",
        default=None,
        help="body formatting, separated by ','",
    )
    email_msg_args.add_argument(
        "-t",
        "--token",
        type=str,
        nargs='+', 
        action='append',
        default=None,
        help="replace token with regex pattern \"\\{[A_Z]_\\}\" in mail body. [[\"{TOKEN}\",\"value\"]]"
    )

    args = parser.parse_args()

    assert pathlib.Path("./timestamp.json").is_file, "./timestamp.json was not found" 
    assert pathlib.Path("./blacklist.json").is_file, "./blacklist.json was not found" 
    assert pathlib.Path("./config.json" if not args.config_file_path else args.config_file_path.strip().strip("\n")), "config.json was not found"

    email_account, email_contents, email_settings = load_config("./config.json" if not args.config_file_path else args.config_file_path)

    if args.delivery_report: email_settings.delivery_report = True; print(f"{Y}[info] Delivery report enabled.{W}")
    if args.subject: email_contents.subject = args.subject
    if args.attachment_path: email_contents.attachments = [Attachment(**load_attachment(attachment_path)) for attachment_path in args.attachment_path.split(",")]
    if args.body: email_contents.set_body(args.body)
    if args.body_format: email_contents.format_body(*args.body_format.strip().strip("\n").split(","))
    if args.force: email_settings.force_sending = args.force

    if args.token:
        if len(args.token) != len(list(set([t[0] for t in args.token]))): raise Exception("got duplicate tokens, review -t|--token arguments.")
        replace_tokens: dict = {t[0]:t[1] for t in args.token}
        email_contents.replace_tokens(replace_tokens)
    else:
        if (email_contents.body_tokens):
            raise Exception(f"got email body with tokens {email_contents.get_tokens(True)}, but no token replacement were provided!")

    print(f"[INFO] Subject: {email_contents.subject}")
    print(f"[INFO] Body path: {None if not args.body else args.body if File.is_file(args.body) else 'NOT A PATH'}")
    print(f"[INFO] Attachment path: {[att.path for att in email_contents.attachments]}")


    mailing_list = get_mailing_list(args.mailList, *[int(range) for range in args.range.split("-")] if args.range else [1, 0])

    em = EasyMail(email_account, email_settings)
    em.send_email(mailing_list, email_contents)
    em.log_report()
