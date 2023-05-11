import argparse, sys

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
        "--body-path",
        default=None,
        help="Email message body path, can be HTML file, or TXT file.",
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

    args = parser.parse_args()

    assert pathlib.Path("./timestamp.json").is_file, "./timestamp.json was not found" 
    assert pathlib.Path("./blacklist.json").is_file, "./blacklist.json was not found" 
    assert pathlib.Path("./config.json" if not args.config_file_path else args.config_file_path.strip().strip("\n")), "config.json was not found"

    email_account, email_message_contents, easy_mail_settings = load_config("./config.json" if not args.config_file_path else args.config_file_path)

    if args.delivery_report: easy_mail_settings.delivery_report = True; print(f"{Y}[info] Delivery report enabled.{W}")
    if args.subject: email_message_contents.subject = args.subject
    if args.attachment_path: email_message_contents.attachments = [Attachment(**load_attachment(attachment_path)) for attachment_path in args.attachment_path.split(",")]
    if args.body_path: email_message_contents.change_body_path(args.body_path)
    if args.body_format: email_message_contents.format_body(*args.body_format.strip().strip("\n").split(","))
    if args.force: easy_mail_settings.force_sending = args.force
        
    print(f"[INFO] Subject: {email_message_contents.subject}")
    print(f"[INFO] Body: {email_message_contents.body_path}")
    print(f"[INFO] Attachment path: {[att.path for att in email_message_contents.attachments]}")

    mailing_list = get_mailing_list(args.mailList, *[int(range) for range in args.range.split("-")] if args.range else [1, 0])

    em = EasyMail(email_account, easy_mail_settings)
    em.send_email(mailing_list, email_message_contents)
    em.log_report()
