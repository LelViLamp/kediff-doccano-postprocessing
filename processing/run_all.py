import step1_unzip
import step2_all_annotations_in_one_file
import step3_automatic_cleaning
import step4a_manually_handle_odd_cases as s4a

print("",
      "************************************************************************************",
      f"Please see \"{s4a.long_annotations_path}\"",
      f"to manually check long annotations and then press any key in the console",
      "************************************************************************************",
      "",
      sep='\n')
input("Decide which long annotations to remove, then press any key to continue processing: ")
print("")

import step4b_handle_long_annotations
import step5a_generate_union_dataset
import step5b_merge_documents
