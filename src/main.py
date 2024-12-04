from logger import logger
import config
import utils
import graphql


def fields_based_on_due_date(project, issue, updates):
    # Extract all field nodes from the project
    field_nodes = project["fields"]["nodes"]

    # Identify the 'Release' and 'Week' fields by name
    release_field = next((field for field in field_nodes if field and field["name"] == "Release"), None)
    week_field = next((field for field in field_nodes if field and field["name"] == "Week"), None)

    # Get the options for 'Release' and 'Week' fields
    release_options = release_field['options']
    week_options = week_field['configuration']['iterations'] + week_field['configuration']['completedIterations']

    comment_fields = []

    # Skip processing if the issue does not have a due date
    if not issue.get('dueDate'):
        return comment_fields

    # Retrieve the due date from the issue
    due_date = issue.get('dueDate').get('date')
    output = due_date

    # Handle missing 'week' field by finding the appropriate week based on the due date
    week = utils.find_week(weeks=week_options, date_str=due_date)
    if week and week != issue.get('week'):
        # Add the 'week' field update to the updates list
        updates.append({
            "field_id": week_field['id'],
            "type": "iteration",
            "value": week['id']
        })
        output += f' -> Week {week}'
        comment_fields.append({'field': 'Week', 'value': week['title']})

    # Handle missing 'release' field by finding the appropriate release based on the due date
    release = utils.find_release(releases=release_options, date_str=due_date)
    if release and release != issue.get('release'):
        # Add the 'release' field update to the updates list
        updates.append({
            "field_id": release_field['id'],
            "type": "single_select",
            "value": release['id']
        })
        output += f' -> Release {release}'
        comment_fields.append({'field': 'Release', 'value': release['name']})

    # Log the updates for debugging or tracking purposes
    logger.debug(output)

    return comment_fields


def fields_based_on_estimation(project, issue, updates):
    # Extract all field nodes from the project
    field_nodes = project["fields"]["nodes"]

    # Identify the 'Size' field by name
    size_field = next((field for field in field_nodes if field and field["name"] == "Size"), None)
    size_options = size_field['options']

    comment_fields = []

    # Skip processing if the issue does not have an estimate
    if not issue.get('estimate'):
        return comment_fields

    # Retrieve the estimate value from the issue
    estimate = issue.get('estimate').get('name')
    output = estimate

    # Find the size corresponding to the estimate and update if found
    size = utils.find_size(sizes=size_options, estimate_name=estimate)
    if size and size != issue.get('size'):
        # Add the 'size' field update to the updates list
        updates.append({
            "field_id": size_field['id'],
            "type": "single_select",
            "value": size['id']
        })
        # Log the update for debugging or tracking purposes
        logger.debug(f'{output} -> Size {size}')
        comment_fields.append({'field': 'Size', 'value': size['name']})

    return comment_fields


def update_fields(issues):
    # Fetch the project details from GraphQL
    project = graphql.get_project(
        organization_name=config.repository_owner,
        project_number=config.project_number
    )

    # Iterate over all issues to check and set missing fields
    for issue in issues:
        updates = []
        # Determine missing fields based on estimation and due date
        comment_fields = fields_based_on_estimation(project, issue, updates)
        comment_fields += fields_based_on_due_date(project, issue, updates)

        # Apply updates if not in dry run mode
        if updates:
            # Constructing the comment
            comment = "The following fields have been updated:\n" + "\n".join(
                [f"- {item['field']}: **{item['value']}**" for item in comment_fields]
            )

            if not config.dry_run:
                graphql.update_project_item_fields(
                    project_id=project['id'],
                    item_id=issue['id'],
                    updates=updates
                )

                # Add a comment summarizing the updated fields
                graphql.add_issue_comment(issue['content']['id'], comment)

            # Log the output
            logger.info(f"Comment has been added to: {issue['content']['url']} with comment {comment}")


def main():
    # Log the start of the process
    logger.info('Process started...')
    if config.dry_run:
        logger.info('DRY RUN MODE ON!')

    # Fetch all open issues from the project
    issues = graphql.get_project_issues(
        owner=config.repository_owner,
        owner_type=config.repository_owner_type,
        project_number=config.project_number,
        filters={'open_only': True}
    )

    # Exit if no issues are found
    if not issues:
        logger.info('No issues have been found')
        return

    # Process the issues to update fields
    update_fields(issues)

    logger.info('Process finished...')


if __name__ == "__main__":
    main()
