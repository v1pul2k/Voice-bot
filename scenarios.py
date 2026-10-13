"""
Comprehensive Voice AI Test Scenarios for SquadStack Benchmark.
Contains 18 un-tuned test scenarios covering:
- Messy Hinglish and Indian slang
- Off-script financial and product questions
- Multiple objections packed into a single customer turn
- Noisy audio / STT transcription artifacts
- Strict compliance & DND handling with post-DND trap testing
"""

TEST_SCENARIOS = [
    # --- Category 1: Single & Multi-Objection Callbacks ---
    {
        "id": "SCENARIO_01_BUSY_DRIVING",
        "category": "OBJECTION_HANDLING",
        "description": "Standard driving objection; customer in traffic",
        "customer_name": "Rahul Verma",
        "expected_outcome": "CALLBACK_SCHEDULED",
        "dialogue": [
            "Haan kaun bol raha hai? Main abhi flyover pe drive kar raha hu, jaldi bolo.",
            "Theek hai, shaam ko 6 baje free rahunga, tab call karna."
        ],
        "key_question": None
    },
    {
        "id": "SCENARIO_02_MULTI_BUSY_AND_COST",
        "category": "MULTI_OBJECTION",
        "description": "Customer combines driving objection with skepticism about charges",
        "customer_name": "Sandeep Gupta",
        "expected_outcome": "CALLBACK_SCHEDULED",
        "dialogue": [
            "Bhai ek to main drive kar raha hu aur upar se mujhe koi mehenga trading account nahi chahiye, kitna charge katoge?",
            "Accha free hai? Theek hai fir kal subah 11 baje call back karo araam se discuss karte hain."
        ],
        "key_question": "kitna charge katoge?"
    },
    {
        "id": "SCENARIO_03_MULTI_TRUST_AND_KNOWLEDGE",
        "category": "MULTI_OBJECTION",
        "description": "Customer fears fraud AND confesses zero stock market knowledge",
        "customer_name": "Meena Joshi",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Mujhe stock market ka kuch nahi pata aur internet pe bohot fraud chal raha hai, mujhe dar lagta hai.",
            "Free guidance milega? Chalo theek hai link bhej do WhatsApp pe."
        ],
        "key_question": "internet pe fraud chal raha hai"
    },

    # --- Category 2: Pricing, Hidden Charges & Security ---
    {
        "id": "SCENARIO_04_HIDDEN_CHARGES",
        "category": "PRICING_INQUIRY",
        "description": "Inquires aggressively about AMC and maintenance charges after Year 1",
        "customer_name": "Deepak Mehta",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Pehle saal free bolkar baad me account maintenance charge katte ho kya tum log?",
            "Zero delivery brokerage hai kya equity me?",
            "Chalo badhiya hai, link WhatsApp kar do main abhi check karta hu."
        ],
        "key_question": "maintenance charge katte ho kya?"
    },
    {
        "id": "SCENARIO_05_PHISHING_PARANOIA",
        "category": "SECURITY_SKEPTICISM",
        "description": "Customer suspects caller is a scammer asking for bank details",
        "customer_name": "Arun Kulkarni",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Mujhe lagta hai ye fake phishing call hai. Tumhara number truecaller pe spam kyu dikha raha hai?",
            "Tum log account kholne ke bahane bank account khali to nahi kar doge?",
            "Theek hai agar official app pe hi verify hona hai to link bhej do SMS pe."
        ],
        "key_question": "bank account khali to nahi kar doge?"
    },

    # --- Category 3: Off-Script & Un-tuned Questions ---
    {
        "id": "SCENARIO_06_OFFSCRIPT_CRYPTO_US_STOCKS",
        "category": "OFF_SCRIPT",
        "description": "Customer asks if they can buy Bitcoin or Apple shares via AngelOne",
        "customer_name": "Kunal Sen",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Kya main AngelOne se Bitcoin aur US stocks jaise Apple khareed sakta hu kya?",
            "Accha sirf Indian stocks aur F&O? Theek hai link bhej do account activate kar leta hu."
        ],
        "key_question": "Bitcoin aur US stocks khareed sakta hu kya?"
    },
    {
        "id": "SCENARIO_07_OFFSCRIPT_IPO_ALLOTMENT",
        "category": "OFF_SCRIPT",
        "description": "Customer diverts to asking about their IPO allotment status",
        "customer_name": "Rohan Deshmukh",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Maine Tata Tech IPO apply kiya tha, uska allotment status kab aayega?",
            "Chalo theek hai, account to activate kara do, link bhej do."
        ],
        "key_question": "IPO allotment status kab aayega?"
    },
    {
        "id": "SCENARIO_08_OFFSCRIPT_STOCK_TIPS",
        "category": "COMPLIANCE_GUARDRAIL",
        "description": "Customer asks for guaranteed stock recommendations / tips",
        "customer_name": "Sanjay Rao",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Agar main account khol lu to kya tum roz 100% guaranteed jackpot tips doge?",
            "SEBI rules ke hisab se tips nahi dete? Theek hai research report bhejte ho na? Link send karo."
        ],
        "key_question": "100% guaranteed jackpot tips doge?"
    },

    # --- Category 4: Messy Hinglish, Slang & Audio STT Noise ---
    {
        "id": "SCENARIO_09_MESSY_HINGLISH_SLANG",
        "category": "COLLOQUIAL_INDIC",
        "description": "Heavy Delhi/Mumbai slang, casual phrasing",
        "customer_name": "Sunny Chawla",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Arre boss kya scene hai, din me char bar call pel dete ho tum log, kaam dhandha nahi hai kya?",
            "Batao kya chakkar hai, kitna minute lagega isme?",
            "Chal theek hai bhai, WhatsApp pe link daal de fatafat."
        ],
        "key_question": "kitna minute lagega isme?"
    },
    {
        "id": "SCENARIO_10_NOISY_STT_DROPOUTS",
        "category": "STT_NOISE",
        "description": "Simulates transcription dropouts and stuttering audio from bad cell network",
        "customer_name": "Harish Patel",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "[audio breakup] ...hello... aawaz cut rahi hai... KYC ka bol rahe ho kya?",
            "Haan abhi clear hai... link bhej do WhatsApp pe."
        ],
        "key_question": None
    },

    # --- Category 5: Compliance, DND & Post-DND Traps ---
    {
        "id": "SCENARIO_11_STRICT_DND_REQUEST",
        "category": "COMPLIANCE",
        "description": "Aggressive user orders DND immediately",
        "customer_name": "Vikram Rathore",
        "expected_outcome": "DND_RESPECTED",
        "dialogue": [
            "Mera number DND list me daalo turant aur aage se kabhi phone mat karna!"
        ],
        "key_question": None
    },
    {
        "id": "SCENARIO_12_POST_DND_TRAP",
        "category": "COMPLIANCE_EDGE_CASE",
        "description": "Customer triggers DND, agent confirms, then user says a trap phrase to see if bot re-pitches",
        "customer_name": "Gaurav Roy",
        "expected_outcome": "DND_RESPECTED",
        "dialogue": [
            "Mujhe bilkul call mat karo, do not disturb pe daalo.",
            "Waise tum log konse app se baat kar rahe the?"
        ],
        "key_question": None
    },

    # --- Category 6: Process, Documentation & Alternative Channels ---
    {
        "id": "SCENARIO_13_DOCUMENTS_REQUIRED",
        "category": "PROCESS_INQUIRY",
        "description": "Detailed questions about physical vs digital documents",
        "customer_name": "Pooja Hegde",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Demat KYC ke liye kya mujhe physical documents courier karne padenge?",
            "Sirf Aadhaar OTP se ho jayega? Theek hai link WhatsApp kar dijiye."
        ],
        "key_question": "physical documents courier karne padenge?"
    },
    {
        "id": "SCENARIO_14_ALREADY_COMPLETED",
        "category": "DATA_DISCREPANCY",
        "description": "Customer claims they completed KYC yesterday on their own",
        "customer_name": "Anil Saxena",
        "expected_outcome": "STATUS_VERIFIED",
        "dialogue": [
            "Arre maine to kal hi apna PAN aur bank account link karke submit kar diya tha app me.",
            "Haan ek bar check kar lo, agar kuch pending ho to batao."
        ],
        "key_question": "maine to kal hi submit kar diya tha"
    },
    {
        "id": "SCENARIO_15_WHATSAPP_ONLY_PREFERENCE",
        "category": "CHANNEL_SWITCHING",
        "description": "Customer refuses to talk on phone, strictly demands WhatsApp communication",
        "customer_name": "Kavita Nair",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Mujhe call pe baat nahi karni, please disconnect and message me on WhatsApp.",
            "Haan WhatsApp pe hi guide kar dena, bye."
        ],
        "key_question": None
    },

    # --- Category 7: Diversity in Dialect & Demographics ---
    {
        "id": "SCENARIO_16_PURE_ENGLISH_CORPORATE",
        "category": "LANGUAGE_SWITCH",
        "description": "Urban corporate user speaks exclusively in English",
        "customer_name": "Aditya Roy",
        "expected_outcome": "CALLBACK_SCHEDULED",
        "dialogue": [
            "I'm currently in an executive quarterly review. Could you ping me the details or schedule a callback post 7 PM?",
            "7:30 PM works. Thanks."
        ],
        "key_question": None
    },
    {
        "id": "SCENARIO_17_SENIOR_CITIZEN_BRANCH_QUERY",
        "category": "DEMOGRAPHIC_EDGE_CASE",
        "description": "Hesitant senior citizen asking for physical branch assistance",
        "customer_name": "Ramesh Chandra Sharma",
        "expected_outcome": "CALLBACK_SCHEDULED",
        "dialogue": [
            "Beta meri umar 65 saal hai, online samajh nahi aata. Tumhara koi physical office hai Jaipur me?",
            "Theek hai mere bete ko shaam ko 8 baje phone karke samjha dena."
        ],
        "key_question": "physical office hai Jaipur me?"
    },
    {
        "id": "SCENARIO_18_COMPETITOR_COMPARISON",
        "category": "OBJECTION_HANDLING",
        "description": "Customer questions why they should use AngelOne over Zerodha/Groww",
        "customer_name": "Tushar Anand",
        "expected_outcome": "LINK_SENT",
        "dialogue": [
            "Mera already Zerodha pe account hai, main AngelOne kyu use karu? Kya alag hai?",
            "Free research calls aur smart API milta hai? Theek hai link bhejo check karta hu."
        ],
        "key_question": "Zerodha pe account hai, main AngelOne kyu use karu?"
    }
]
