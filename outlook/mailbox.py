import json

import requests
from outlook.auth import init_o365

account = init_o365()
print("Account: ", account)

mailbox = account.mailbox()
print("Mailbox: ", mailbox)

inbox = mailbox.inbox_folder()
print("Inbox: ", inbox)

messages = inbox.get_messages(limit=20)
print("Messages: ", messages)

for i in messages:
    if i.has_attachments:
        m = i
        break
print("message: ", m)

success = m.attachments.download_attachments()
m_id = m.object_id
for a in m.attachments._BaseAttachments__attachments:
    url = a._base_url + a._endpoints.get('attachment').format(id=m_id, ida=a.attachment_id)
    response = account.con.get(url)
    content = json.loads(response.content)
    with open(content.get("Name"), 'wb') as f:
        f.write(bytes(content.get("ContentBytes"), encoding='utf-8'))

print(success)
