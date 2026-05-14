import re


REPLY_PATTERNS = [

    r"-----Original Message-----",



    r"On .* wrote:",

    r"Begin forwarded message:",

    r"________________________________",

    r"CAUTION:.*",

    r"This email and any attachments.*",

]


SIGNATURE_PATTERNS = [

    r"Best regards,.*",
    r"Regards,.*",
    r"Thanks,.*",
    r"Sincerely,.*",

]


def strip_quoted_reply(
    text: str,
) -> str:

    if not text:
        return ""

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        matched = False

        for pattern in REPLY_PATTERNS:

            if re.search(
                pattern,
                line,
                re.IGNORECASE,
            ):

                print(
                    "✂️ QUOTED REPLY STRIPPED:",
                    line[:100]
                )

                matched = True
                break

        if matched:
            break

        cleaned.append(line)

    result = "\n".join(
        cleaned
    )

    # ---------------------------------------
    # 🔥 OPTIONAL SIGNATURE TRIM
    # ---------------------------------------

    for pattern in SIGNATURE_PATTERNS:

        m = re.search(
            pattern,
            result,
            re.IGNORECASE | re.DOTALL,
        )

        if m:

            result = result[:m.start()].strip()

    return result.strip()